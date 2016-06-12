library(quantmod)


cat('ok')

ticker <- 'ZS000001'

threshold <- 0.1
path <- '/dayk/'

gpath <- paste('/Users/liu/apps/qts/pytrade/data', path, ticker,'.gd.csv',sep='')
gd <- read.csv(gpath,colClasses=c('character','numeric'),head=TRUE,sep=",")

qpath <- paste('/Users/liu/apps/qts/pytrade/data',path,sep='')
quotes <- getSymbols(ticker, dir= qpath, src="csv", env= data, auto.assign=FALSE)
quotes <- quotes['2015-08::']

hpath <- paste('/Users/liu/apps/qts/pytrade/data',path, ticker,'.hcluster.csv',sep='')
hls <- read.csv(hpath,colClasses=c('numeric','numeric', 'numeric', 'numeric', 'numeric'),head=TRUE,sep=",")


peekpath <- paste('/Users/liu/apps/qts/pytrade/data', path, ticker,'.peek.csv',sep='')
peek <- read.csv(peekpath,colClasses=c('character','numeric','numeric','numeric'),head=TRUE,sep=",")



# 收集顶点
peekres <- c()
peekval <- c()
for (g in peek$Date){
	x0 <- which(index(quotes) == g)[1] 
	if(!is.na(x0)){
		peekres <- c(peekres, x0)
		peekval <- c(peekval, peek$val[peek$Date==g])
	}
}
# 配对顶点，计算顶点插值
peekline = rep(NA, length(index(quotes)))
x0 <- peekres[3]
x1 <- peekres[2]
y0 <- peekval[3]
y1 <- peekval[2]
peekdiff = seq(y0,y1, (y1 - y0)/(x1-x0))
peekline[x0] = y0
peekline[x1] = y1
peekline[(x0+1):(x1-1)] = peekdiff[2:(x1-x0)]

peekright <- c()
tmp <- y1
for(i in x1:length(index(quotes))){
	tmp <- tmp + (i-x1) * (y1 - y0) / (x1 -x0); 
	peekright <- c(peekright, tmp)
}
peekline[x1:length(index(quotes))] <- peekright[1:length(peekright)]




peekPlot = function (x, n = 1, wilder = FALSE, ratio = NULL){
	ma <- .Call("ema", x, n, ratio, PACKAGE = "TTR")
	ma <- c(peekline)
    reclass(ma, x)
}

# newEMA2 <- newTA(peekPlot, Cl, on=1, col=1, lwd=2)
# plot(newEMA2())