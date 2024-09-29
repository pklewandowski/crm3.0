class HierarchyUtils {
    static findNode(nodeStructure, nodeId) {
        let result = null;

        function f(nodes) {
            for (let n of nodes) {
                if (n.id == nodeId) {
                    result = n;
                    break;
                }
                if (n.children.length) {
                    f(n.children);
                }
            }
        }

        if (nodeStructure.id == nodeId) {
            return nodeStructure;
        }

        f(nodeStructure.children);

        return result;
    }

    static isChild(nodeStructure, node) {
        for (let n of nodeStructure.children) {
            if (node.id === n.id) {
                return true;
            }
            if(n.children.length) {
                HierarchyUtils.isChild(n, node);
            }
        }
    }
}

export {HierarchyUtils};