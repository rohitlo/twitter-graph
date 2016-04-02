#!/usr/bin/env Rscript
require(ggplot2)
data <- read.csv('analysis/data.csv')
p <- ggplot(data, aes(x=tweets, y=total.time, color=kind)) +
  geom_point() +
  coord_trans(x='log2',y='log2') +
  theme(axis.text.x=element_text(angle=90, hjust=1))

#png('plot.png')
pdf('plot.pdf')
p
dev.off()
