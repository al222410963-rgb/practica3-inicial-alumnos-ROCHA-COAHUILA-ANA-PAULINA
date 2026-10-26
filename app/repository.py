"""Repositorio en memoria del Catálogo de Productos."""

from .schemas import Categoria, ProductoIn, ProductoOut


class SkuDuplicado(Exception):
    """Ya existe otro producto con ese SKU."""


class ExistenciasInsuficientes(Exception):
    """El ajuste dejaría las existencias en negativo."""


class ProductoRepository:
    def __init__(self) -> None:
        self._items: dict[int, ProductoOut] = {}
        self._next_id = 1

    def add(self, data: ProductoIn) -> ProductoOut:
        # Verificar que el SKU no esté registrado.
        for producto in self._items.values():
            if producto.sku == data.sku:
                raise SkuDuplicado()

        # Crear el producto.
        producto = ProductoOut(
            id=self._next_id,
            sku=data.sku,
            nombre=data.nombre,
            precio=data.precio,
            existencias=data.existencias,
            categoria=data.categoria,
            disponible=data.existencias > 0,
        )

        self._items[self._next_id] = producto
        self._next_id += 1

        return producto

    def list(
        self, categoria: Categoria | None = None, solo_disponibles: bool = False
    ) -> list[ProductoOut]:
        productos = list(self._items.values())

        if categoria is not None:
            productos = [
                producto
                for producto in productos
                if producto.categoria == categoria
            ]

        if solo_disponibles:
            productos = [
                producto for producto in productos if producto.disponible
            ]

        return productos

    def get(self, producto_id: int) -> ProductoOut | None:
        return self._items.get(producto_id)

    def update(self, producto_id: int, data: ProductoIn) -> ProductoOut | None:
        # Comprobar que el producto exista.
        if producto_id not in self._items:
            return None

        # Comprobar que otro producto no tenga el mismo SKU.
        for otro_id, producto in self._items.items():
            if otro_id != producto_id and producto.sku == data.sku:
                raise SkuDuplicado()

        # Actualizar conservando el mismo ID.
        producto_actualizado = ProductoOut(
            id=producto_id,
            sku=data.sku,
            nombre=data.nombre,
            precio=data.precio,
            existencias=data.existencias,
            categoria=data.categoria,
            disponible=data.existencias > 0,
        )

        self._items[producto_id] = producto_actualizado

        return producto_actualizado

    def delete(self, producto_id: int) -> bool:
        return self._items.pop(producto_id, None) is not None

    def ajustar_existencias(
        self, producto_id: int, cantidad: int
    ) -> ProductoOut | None:
        # Comprobar que el producto exista.
        producto = self._items.get(producto_id)

        if producto is None:
            return None

        nuevas_existencias = producto.existencias + cantidad

        # Evitar que las existencias queden en negativo.
        if nuevas_existencias < 0:
            raise ExistenciasInsuficientes()

        # Actualizar existencias y disponibilidad.
        producto_actualizado = producto.model_copy(
            update={
                "existencias": nuevas_existencias,
                "disponible": nuevas_existencias > 0,
            }
        )

        self._items[producto_id] = producto_actualizado

        return producto_actualizado


repo = ProductoRepository()


def get_repo() -> ProductoRepository:
    return repo
