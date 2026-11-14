# TIPS

data structure

用的是邻接表来存储图的节点和边

优化的原理和基础：

在Dijkstra算法的实现中，使用堆（特别是最小堆）可以显著优化寻找当前未访问顶点中具有最小距离估计的顶点这一过程。原始的Dijkstra算法在每一步都需要从所有未访问的顶点中选出距离最小的顶点，如果直接遍历所有顶点来找到这个最小距离顶点，这一步的时间复杂度是O(V)，其中V是顶点的数量。对于算法的整体执行来说，这部分就会有O(V^2)的时间复杂度，对于较大的图来说可能非常慢。

通过使用最小堆（优先队列）来存储所有未访问的顶点，堆顶元素总是当前未访问顶点中距离最小的那个，这样就可以在O(1)时间复杂度内获得当前最小距离的顶点。

Fib

不用时刻保持严格二项堆的性质

删除后才维护二项堆的性质

>- 初始化一个度数表，用来跟踪具有特定度数的树。
>- 遍历根链表中的每个节点。对于每个节点，检查其度数是否与度数表中已存在的树冲突。
>- 如果没有冲突，将该节点加入度数表。
>- 如果有冲突，即度数表中已有一个或多个具有相同度数的树，则将这些树进行一次链接操作，即将其中一个树的根节点作为另一个树根节点的子节点。链接操作会导致树的度数增加。
>- 重复这一过程，直到根链表中所有的树都被处理，且度数表中不再有任何冲突。

把所有节点插入Fib堆，用Fib来删除最小节点，然后维护，然后删除最小节点，一直循环，直到Dijkstra完成

## testing部分

全是连通图

## conclusion部分

Fib

t(H)树的数量

m(H)已标记节点数量

The number of delete-min operation is atmost E because our size of the heap is atmost E and we need to output all those nodes in the heap no matter that node is visited or not. And in the worst case we need to update all edges we could when visiting a particular node, so the number of insert operation is also E. The conclution is the time cost of the hole algorithm is O(Elog E + E logE) for min heap, O(log E + E logE) for fib heap and lefist heap. In our case the number of edges are merely 2 to 3 time of the number of nodes. So the time complexity of three implementations are both o(VlogV).

space

邻接表跟E和V有线性关系

Heap的结构和E有线性关系