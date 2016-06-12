test = function (x, n = 10, wilder = FALSE, ratio = NULL)
{
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
    ma[1:100] = NA

    ma[102:1999] = NA

  
    ma[2001:4000] = NA
   
    diff = seq(ma[101],ma[2000], (ma[2000] - ma[101])/(2000-101+1))

    ma[102:1999] = diff[2:(2000-101)]
    # reclass(ma, x)
}

getSymbols('SBUX')
barChart(SBUX)
newEMA <- newTA(test, Cl, on=1, col=4, lwd=2)
plot(newEMA())


