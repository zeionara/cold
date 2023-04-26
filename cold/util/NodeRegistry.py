from .NodeFactory import NodeFactory


class NodeRegistry:
    def __init__(self, factory: NodeFactory, directed: bool = True):
        self.factory = factory
        self.cache = {}

        self.directed = directed
        self.not_directed = not directed

    def get_node(self, name: str, type_: str, /):
        if (objects_with_the_same_type := self.cache.get(type_)) is None:
            self.cache[type_] = {name: (node := self.factory.make(name, type_))}
            return node
        if (object_with_the_same_name := objects_with_the_same_type.get(name)) is None:
            objects_with_the_same_type[name] = node = self.factory.make(name, type_)
            return node
        return object_with_the_same_name

    def push(self, triple: tuple, get_backward_link: callable = None):
        ((lhs_name, lhs_type), link, (rhs_name, rhs_type)) = triple

        lhs = self.get_node(lhs_name, lhs_type)
        rhs = self.get_node(rhs_name, rhs_type)

        lhs.push(link, rhs)

        if self.not_directed:
            rhs.push(link, lhs)
        elif get_backward_link is not None and (backward_link := get_backward_link(lhs_type, rhs_type, link)) is not None:
            rhs.push(backward_link, lhs)
        # elif self.not_directed:
        #     rhs.push(link if get_backward_link is None else get_backward_link(lhs_type, rhs_type, link), lhs)

    @property
    def flat_cache(self):
        return {
            'nodes': tuple(
                node
                for type_key, type_nodes in self.cache.items()
                for node_key, node in type_nodes.items()
            )
        }
