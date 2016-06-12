
path <- '/backtests/'

ticker <- '20110104_20111230.rets'
gpath <- paste('/Users/liu/apps/qts/pytrade/', path, ticker,'.csv',sep='')
rets <- read.csv(gpath,colClasses=c('character','numeric','numeric','numeric','numeric','numeric'),head=TRUE,sep=",")

gpath <- paste('/Users/liu/apps/qts/pytrade/', '', 'tmp','.tmp',sep='')
point <- read.csv(gpath, colClasses =c('character'), head=FALSE, sep=",")

mark <- c()
x <- rets$day
for(i in seq(length(point$V1))){
	p <- point$V1[i]
	for (j in seq(length(x))){
		if(p == x[j]){
			break
		}
	}
	mark <- c(mark, j)
	j <- 1
}
y <- rets$sz000001
plot(y,type='l',ylim=c(-25,20))
lines(rets$ret2,type='l',col='blue')
points(mark, y[mark], type='p', col='red')
