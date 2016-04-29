dev.off()
par(mfrow=c(17,17))
par(mar=c(0.0,0.0,0.0,0.0))
acc_data <- read.csv(file="/home/jrc/confusion.csv", stringsAsFactors=FALSE)
par(bg="WHITE")
for (i in 1:289) {
      percent = acc_data[i, 3]
      num = round((1-percent) * 100)
      color = paste("GRAY", num, sep="")
      barplot(acc_data[i,3], axes=FALSE, main="", ylim = range(0.0,1.0), col="WHITE", border=NA)
      text(0.75, 0.25, acc_data[i,3], col=color)
}