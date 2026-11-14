# LAB1 REPORT

### CODE

```
0011 0000 0000 0000     ; (.ORIG x3000)
0010 000 01111 1111     ; LD R0, x3100
0101 011 011 1 00000    ; AND R3, R3, #0 SET R3 TO 0
0001 011 011 1 00001    ; ADD R3, R3, #1
0101 100 100 1 00000    ; AND R4, R4, #0
0000 111 000000011      ; BRnzp 'NEXT'+2
0101 100 100 1 00000    ; AND R4, R4, #0 SET R4 TO 0 'RESET'
0001 011 011 000 011    ; ADD R3, R3, R3  DOUBBLE R3 'NEXT'
0000 010 000000111      ; BRz END1 PC+7
0101 001 000 000 011    ; AND R1, R0, R3
0000 001 000000001      ; BRp COUNT PC+1
0000 010 111111010      ; BRz RESET PC-6
0001 100 100 1 00001    ; ADD R4, R4, #1 COUNT THE NUMBER OF CONSECUTIVE 1 'COUNT'
0001 101 100 1 11101    ; ADD R5, R4, #(-3) CHECK IF THIS IS THE THIRD 1
0000 010 000000011      ; BRz END2 PC+3
0000 100 111110111      ; BRn NEXT PC-9
0101 010 010 1 00000    ; AND R2, R2, #0 SET R2 TO 0 'END1'
1111 0000 00100101      ; HALT
0101 010 010 1 00000    ; AND R2, R2, #0 SET R2 TO 0 'END2'
0001 010 010 1 00001    ; ADD R2, R2, #0 SET R2 TO 1
1111 0000 00100101      ; HALT
```

### Pseudocode

```pseudocode
Begin
    R0<-M[x3100]
    R3<-1
    R4<-0
    R2<-0
	while R3<=65,536
    begin
        if R3!=1 then R3<-R3*2
        R1<-R0 && R3
        	if R1>0 then
            begin
                R4<-R4+1
                    if R4==3 then
                    begin
                        R2:=1
                        break
                    end
            end
            else if R1==0 then
            begin
            	R4<-0
            end
    end
    output R2

End
```

### Problems I met

While debugging, after running the program with random values, an error occurred. Upon inspection, it was found that the R4 register was not initialized. Consequently, the statement `AND R4, R4, #0` was added to initialize R4.

### Questions

1. How many times will the loop iterate if the data in x3100 is 1110 0000 0000 0000

Answer: 16 times.

2. How many times will the loop iterate if the data in x3100 doesn't contain '111'

Answer: 16 times.