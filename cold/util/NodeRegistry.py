from .NodeFactory import NodeFactory


class NodeRegistry:
    def __init__(self, factory: NodeFactory):
        self.factory = factory
        self.cache = {}

    def get_node(self, name: str, type_: str, /):
        if (objects_with_the_same_type := self.cache.get(type_)) is None:
            self.cache[type_] = {name: (node := self.factory.make(name, type_))}
            return node
        if (object_with_the_same_name := objects_with_the_same_type.get(name)) is None:
            objects_with_the_same_type[name] = node = self.factory.make(name, type_)
            return node
        return object_with_the_same_name

    def push(self, triple: tuple):
        ((lhs_name, lhs_type), link, (rhs_name, rhs_type)) = triple

        lhs = self.get_node(lhs_name, lhs_type)
        rhs = self.get_node(rhs_name, rhs_type)

        lhs.push(link, rhs)
