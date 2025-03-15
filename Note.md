2024F的routing不全，换成2025Spring
# L1
- 讲了分层的overview

# L2 Internet Design Principle
- 七条设计原则
- 窄腰：第三层（Internet）只有一种协议---- IP，因此统一了Internet，且其他层有不同的协议，进而使联邦性成为可能
- 解复用：通过在header上加上高层的协议信息，使得其在网络栈上按照正确的途径传输。注意：第四层到第七层即应用层通过端口号解复用。注意与插线的物理端口进行区分
- 一二层在网络接口卡（NIC网卡）上实现，三四层由OS实现
- 端对端原则（David D.Clark）：在终端主机上保证传输的正确性。为什么？因为在两端的检验是必须的，而且不许依赖Networks实现的正确性。但有些时候会在Networks上实现可靠性以优化性能
- 统计复用：共享资源。通常情况下，和需求的最大值 < 需求最大值的和。
- 共享资源的两种形式：circuit switching和packet switching（为什么这玩意翻译成分组交换？）。前者预留，后者尽力而为。在突发性较强的情况下，packet switching效率更高



### Done lec06