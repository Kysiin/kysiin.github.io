# LAB4 REPORT

### Pseudocode

```pseudocode
begin
	initial<-15
	char<-'a'
	flag<-0
    while 1 do
    begin
    	in a		//input i.e.
    				//.ORIG x2000
            		//LDI R1, KBDR_ADDR
            		//AND R3, R3, #0	R3 is used the same as the flag in this Pseudocode
            		//ADD R3, R3, #1
            		//RTI
        if a<='9' then	//input is a number
        begin
            a<-a-'0'
			initial<-initial+a
			if initial>17 then initial<-18
			flag<-1
        end
        else if a>'a' then		//input is a letter
        begin
        	char<-a		//change the output char to the one in input
        end
        if flag==0 then 	//initial hasnt changed by input
        begin
        	initial<-initial-1
        	if initial==-1 then initial<-0
        end
        for i:=1 to initial-1 do	//output air	..............
        begin
        	output '.'
        end
        output char		//output char 3 times	..............aaa
        output char
        output char
        for i:=initial+3 to 20 do	//output air again	..............aaa...
        begin
        	output '.'
        end
        for i:=0 to 25000 do i<-i	//delay part
    end
end
```

>***Explanation already in the code comment.***

### Questions

1. **How does Interrupt service routine work?**

After setting the 14th bit of KBSR to 1, when keyboard input occurs, it will interrupt the program. At this point, the program is executing the DELAY section`for i:=0 to 25000 do i<-i //delay part`, and it will enter the Interrupt Service Routine `in a //input `  where I only read the content of KBDR. Then, the program will return to the DELAY section.

2. **Where does the priority of the Interrupt Service Routine reside?**

In PSR. When the Interrupt Service Routine is executed, which occurs when it is interrupted by keyboard input, the PSR will load the priority of the ISR.

3. **If the Interrupt Service Routine is already running, and another keyboard input is made, how will the ISR execute?**

Since the priorities of the two ISRs are the same, the currently running part of the ISR will continue to execute, and then the second ISR will be executed once.

4. **When running a TRAP instruction, if keyboard input is generated, will the TRAP be interrupted?**

Yes, because TRAP has the same priority as the whole user program, so it will be interrupted.