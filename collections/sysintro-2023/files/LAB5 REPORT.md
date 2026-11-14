# LAB5 REPORT

### Pseudocode

```pseudocode
begin
	in M
	in N
	in THEMAP[]
	R1<-0
	R2<-0
	while R1<=M*N-1 do		//To see if the whole map has been looted
	begin
		RO<-R1
		R1<-R1+1
		call FSTART(R0)
		if R0>R2 then R2<-R0		//If the new distance is longer,put it in R2
	end
FSTART:
	//ADD R6, R6, #-1  The recursive function in LC3 will have to store the registers first
    //STR R1, R6, #0
    //ADD R6, R6, #-1
    //STR R2, R6, #0
    //ADD R6, R6, #-1
    //STR R3, R6, #0
    //ADD R6, R6, #-1
    //STR R4, R6, #0
    //ADD R6, R6, #-1
    //STR R5, R6, #0
    //ADD R6, R6, #-1
    //STR R7, R6, #0
	R3<-0
	if (R0+M)<M*N-1 then	//IF R0+M IS OUT OF MAP
	begin
		if THEMAP[R0]>THEMAP[R0+M] then		//IF THEMAP[R0] IS BIGGER THAN THEMAP[R0+M]
		begin
			call FSTART(R0+M)		//GET THE DISTANCE OF THEMAP[R0+M],which is stored in R0
            if R0>R3 then R3<-R0	//IF THE DISTANCE IS LONGER,PUT IT IN R3
		end
	end
	if (R0-M)>=0 then
	begin
		if THEMAP[R0]>THEMAP[R0-M] then
		begin
			call FSTART(R0-M)
			if R0>R3 then R3<-R0
		end
	end
	if (R0-1) MOD 4 ==0 then
	begin
		if THEMAP[R0]>THEMAP[R0-1] then
		begin
			call FSTART(R0-1)
			if R0>R3 then R3<-R0
		end
	end
	if (R0+1) MOD 4 ==3 then
	begin
		if THEMAP[R0]>THEMAP[R0+1] then
		begin
			call FSTART(R0+1)
			if R0>R3 then R3<-R0
		end
	end
	R0<-R3+1
	return R0
end
```

### Questions

1. How many stacks at most will there be after the program has been executed if THEMAP is M*N.

The longest distance is M*N.

Every time the recursive function is executed, it will use 6 stacks.

​		 ADD R6, R6, #-1
​            STR R1, R6, #0
​            ADD R6, R6, #-1
​            STR R2, R6, #0
​            ADD R6, R6, #-1
​            STR R3, R6, #0
​            ADD R6, R6, #-1
​            STR R4, R6, #0
​            ADD R6, R6, #-1
​            STR R5, R6, #0
​            ADD R6, R6, #-1
​            STR R7, R6, #0

So in total, there will be 6\*M*N stacks at most in the end.