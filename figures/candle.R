library(quantmod)

png('rplot.png', width=400,height=400,res=72)

ticker <- 'ZS000001'
# ticker <- 'SH600787'
# ticker <- 'SH601069'
# ticker <- 'SH600467'
# ticker <- 'SH603019'
# ticker <- 'SZ002195'
# ticker <- 'SZ300406'
# ticker <- 'SZ300315'
# ticker <- 'SZ300329'
# ticker <- 'SZ000001'
# ticker <- 'ZS399006'

threshold <- 0.1

path <- '/dayk/'

gpath <- paste('/Users/liu/apps/qts/pytrade/data', path, ticker,'.gd.csv',sep='')
gd <- read.csv(gpath,colClasses=c('character','numeric'),head=TRUE,sep=",")

qpath <- paste('/Users/liu/apps/qts/pytrade/data',path,sep='')
quotes_raw <- getSymbols(ticker, dir= qpath, src="csv", env= data, auto.assign=FALSE)
quotes <- quotes_raw['2015-12::']

hpath <- paste('/Users/liu/apps/qts/pytrade/data',path, ticker,'.hcluster.csv',sep='')
hls <- read.csv(hpath,colClasses=c('numeric','numeric', 'numeric', 'numeric', 'numeric'),head=TRUE,sep=",")

peekpath <- paste('/Users/liu/apps/qts/pytrade/data', path, ticker,'.ndes.csv',sep='')
peek <- read.csv(peekpath,colClasses=c('character','numeric','character','numeric'),head=TRUE,sep=",")

valleypath <- paste('/Users/liu/apps/qts/pytrade/data', path, ticker,'.ninc.csv',sep='')
valley <- read.csv(valleypath,colClasses=c('character','numeric','character','numeric'),head=TRUE,sep=",")

# IMPORT INIT VARIABLE
nclose <- tail(as.numeric(quotes[, grep("Close", colnames(quotes), ignore.case = TRUE)]),n=1)
headdate <- head(index(quotes), n = 1)
basedate <- tail(index(quotes), n = 1)
minY <- min(quotes[,3])
maxY <- max(quotes[,2])
# Add future points
for (k in seq(20)){
	quotes <- c(quotes,xts(rbind(c(0, 0, 0, 0, 0, 0)), basedate + k))
}


#收集顶点
plines = c()
for(i in seq(length(index(peek)))){
	g1 = peek[i,1]
	v1 = peek[i,2]
	g2 = peek[i,3]
	v2 = peek[i,4]
	peekres <- c()
	peekval <- c()
	t1 <- which(index(quotes_raw) == g1)[1] 
	t2 <- which(index(quotes_raw) == g2)[1] 
	
	if(is.na(t1) || is.na(t2)){
		next
	}
	
# 配对顶点，计算顶点插值
	peekline = rep(NA, length(index(quotes_raw)))
	x0 <- t1
	x1 <- t2
	y0 <- v1
	y1 <- v2
	peekdiff = seq(y0,y1, (y1 - y0)/(x1-x0))
	peekline[x0] = y0
	peekline[x1] = y1
	peekline[(x0+1):(x1-1)] = peekdiff[2:(x1-x0)]
	peekright <- c()
	tmp <- y1
	for(i in x1:length(index(quotes_raw))){
		tmp <- y1 + (i-x1) * (y1 - y0) / (x1 -x0); 
		peekright <- c(peekright, tmp)
	}
	peekline[x1:length(index(quotes_raw))] <- peekright[1:length(peekright)]
	headind <- which(index(quotes_raw)== headdate)
	peekline <- peekline[headind:length(index(quotes_raw))]
	plines <- rbind(plines,peekline)
}

# 收集低点
vlines = c()
for(i in seq(length(index(valley)))){
	g1 = valley[i,1]
	v1 = valley[i,2]
	g2 = valley[i,3]
	v2 = valley[i,4]
	valleyres <- c()
	valleyval <- c()
	t1 <- which(index(quotes_raw) == g1)[1] 
	t2 <- which(index(quotes_raw) == g2)[1] 
	
	if(is.na(t1) || is.na(t2)){
		next
	}
	valleyline = rep(NA, length(index(quotes_raw)))
	x0 <- t1
	x1 <- t2
	y0 <- v1
	y1 <- v2
	valleydiff = seq(y0,y1, (y1 - y0)/(x1-x0))
	valleyline[x0] = y0
	valleyline[x1] = y1
	valleyline[(x0+1):(x1-1)] = valleydiff[2:(x1-x0)]
	valleyright <- c()
	tmp <- y1
	for(i in x1:length(index(quotes_raw))){
		tmp <- y1 + (i-x1) * (y1 - y0) / (x1 -x0); 
		valleyright <- c(valleyright, tmp)
	}
	valleyline[x1:length(index(quotes_raw))] <- valleyright[1:length(valleyright)]
	
	headind <- which(index(quotes_raw)== headdate)
	valleyline <- valleyline[headind:length(index(quotes_raw))]
	vlines <- rbind(vlines, valleyline)
}

# 收集拐点
res <- c()
val <- c()
for (g in gd$Date){
	x0 <- which(index(quotes) == g)[1] 
	if(!is.na(x0)){
		res <- c(res, x0)
		val <- c(val, gd$GD[gd$Date==g])
	}
}

# 计算拐点插值
gdline = rep(NA, length(index(quotes)))
for(i in seq(length(res))){
	if(i == length(res)){
		break
	}
	x0 <- res[i]
	x1 <- res[i+1]
	y0 <- val[i]
	y1 <- val[i+1]
	diff = seq(y0,y1, (y1 - y0)/(x1-x0))
	gdline[x0] = y0
    gdline[x1] = y1
    gdline[(x0+1):(x1-1)] = diff[2:(x1-x0)]
}

# 画拐点图
gdPlot = function (x, n = 1, wilder = FALSE, ratio = NULL){
    x <- try.xts(x, error = as.matrix)
    if (n < 1 || n > NROW(x))
        stop("Invalid 'n'")
    x.na <- xts:::naCheck(x, n)
    if (missing(n) && !missing(ratio))
        n <- trunc(2/ratio - 1)
    if (is.null(ratio)) {
        if (wilder)
            ratio <- 1/n
        else ratio <- 2/(n + 1)
    }
    ma <- .Call("ema", x, n, ratio, PACKAGE = "TTR")
	ma <- gdline
    reclass(ma, x)
}

if(ticker=='ZS000001' || ticker=='ZS399006'){
	# colnames(quotes_raw)[3] <- paste(ticker,".Close",sep="")
	# colnames(quotes)[4] <- paste(ticker,".Low",sep="")
	threshold <- 0.05
}

m <- chartSeries(quotes, name=paste(ticker),line.type = "l",TA=NULL,
	  yrange=c(minY * 0.95,maxY * 1.05),
       theme = chartTheme("white", up.col='red',dn.col="green")) 
    
# debug(test)
newEMA <- newTA(gdPlot, Cl, on=1, col=4, lwd=2)
plot(newEMA())

h <- hls$median
for(i in seq(length(h))){
	if (is.na(nclose)){
		next
	}
	if (abs((nclose - h[i])/(h[i]+0.0000000001)) > threshold){
		next
	}
	hline <- rep(h[i],length(index(quotes_raw)))
	hPlot = function (x, n = 1, wilder = FALSE, ratio = NULL)
	{
		ma <- .Call("ema", x, n, ratio, PACKAGE = "TTR")
		ma <- c(hline)
    	reclass(ma, x)
	}
	newEMA2 <- newTA(hPlot, Cl, on=1, col=6, lwd=2)
	plot(newEMA2())
}

#画peek下降趋势线
bind <- which(index(quotes)== basedate)
if(length(plines) > 0){
for(j in seq(NROW(plines))){
	peekline <- plines[j,]
	if(peekline[bind] < 0 || peekline[bind] < (nclose * 0.90) || peekline[bind] > (nclose*1.10)){
		next
	}
	peekPlot = function (x, n = 1, wilder = FALSE, ratio = NULL){
		ma <- .Call("ema", x, n, ratio, PACKAGE = "TTR")
		ma <- c(peekline)
    	reclass(ma, x)
	}
	newEMA2 <- newTA(peekPlot, Cl, on=1, col=2, lwd=2)
	plot(newEMA2())
}
}

#画valley上升趋势线
bind <- which(index(quotes)== basedate)
for(j in seq(NROW(vlines))){
	valleyline <- vlines[j,]
	if(valleyline[bind] < 0 || valleyline[bind] < (nclose * 0.90) || valleyline[bind] > (nclose*1.10)){
		next
	}
	valleyPlot = function (x, n = 1, wilder = FALSE, ratio = NULL){
		ma <- .Call("ema", x, n, ratio, PACKAGE = "TTR")
		ma <- c(valleyline)
    	reclass(ma, x)
	}
	newEMA2 <- newTA(valleyPlot, Cl, on=1, col='darkorchid', lwd=2)
	plot(newEMA2())
}


title(main="", cex.main=2.5, font.main=4, col.main="gold", 
sub="", cex.sub=1.5, font.sub=4, col.sub="blue", 
xlab="", ylab="",col.lab="blue", cex.lab=1)   

dev.off()
