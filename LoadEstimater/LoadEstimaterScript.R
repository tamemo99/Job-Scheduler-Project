



trainingData <- read.csv(file = "trainingData.csv")

mx <- ts(trainingData$containers , start = 10031)


df <- data.frame(  integer(),
                   integer(),
                   integer(),
                   double(),
                   double(),
                   double())

for(k in c(1,2)){
  for(i in c(1:10)){
    for(j in c(1:10)){
      
      
      result = tryCatch({
        model <- arima(mx,order = c(i,k,j),optim.control = list(maxit = 1000))
        flag <- TRUE
        
      }, warning = function(w) {
        flag <- FALSE
        
      }, error = function(e) {
        flag <- FALSE
        
      }, finally = {
      })
      
      if(!flag){
        next
      }
      
      
      SSE<-sum(model$residuals^2)
      test<-Box.test(model$residuals, lag = log(length(model$residuals)))
      
      if(test$p.value > 0.01){
        x <- data.frame(i, k,j, model$aic, SSE,test$p.value)
        
        df <- rbind(df,x)
      }
      print(paste(i," ",k," ",j))
      
    }
  }
}

colnames(df) <- c('p','d','q','AIC', 'SSE', 'p-value')
order <- df[df$AIC == min(df$AIC),]

ord <- c(order[,1],order[,2],order[,3])
print(ord)

model <- arima(mx,order = ord,optim.control = list(maxit = 1000) )
print(model)


SSE<-sum(model$residuals^2)
test<-Box.test(model$residuals, lag = log(length(model$residuals)))

print(model$aic)
print(SSE)
print(test$p.value)


estimatedLoad <- data.frame(trainingData$time+10000,ceiling(predict(model,n.ahead = 10000)$pred))
names(estimatedLoad) <- c("time","containers")

write.csv(estimatedLoad, file = "EstimatedClusterLoad.csv")




