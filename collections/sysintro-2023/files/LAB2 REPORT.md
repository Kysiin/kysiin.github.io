# LAB2 REPORT

### CODE

```
.ORIG x3000
    LD R1, LOAD1
    LD R2, LOAD2
    LD R4, THIRTYTWO
    LD R5, NNINETYSEVEN
    LD R7, STORE1
    AND R3, R3, #0
    BR NEXT
NEXT2
    ADD R2, R2, #0
    BRz COMPARE
    AND R1, R1, #0
    ADD R1, R1, R2
    AND R2, R2, #0
    AND R3, R3, #0
    LD R7 STORE2
NEXT
    AND R0, R0, #0
    ADD R0, R0, R1
    LDR R0, R0, #0
    ADD R0, R0, R3
    ADD R3, R3, #1
    LDR R0, R0, #0
    BRz NEXT2
    NOT R6, R4
    ADD R6, R6, #1      ;R6=-32
    ADD R6, R0, R6      ;RO?=SPACE
    BRz NEXT
    ADD R6, R6, #-16
    ADD R6, R6, #-16
    BRnz NEXT
    ADD R6, R0, R5
    BRn CONVERT

BACK
    ADD R0, R0, R5
    ADD R6, R7, R0
    LDR R0, R6, #0
    ADD R0, R0, #1
    STR R0, R6, #0
    BR NEXT
CONVERT
    ADD R0, R0, R4
    BR BACK
COMPARE
    LD R1, STORE1
    LD R2, STORE2
    AND R3, R3, #0
    AND R4, R4, #0
LOOP
    ADD R0, R3, #-15
    ADD R0, R0, #-11
    BRz FINISH1
    AND R5, R5, #0
    AND R6, R6, #0
    ADD R5, R1, R3
    LDR R5, R5, #0
    ADD R6, R2, R4
    LDR R6, R6, #0
    ADD R3, R3, #1
    ADD R4, R4, #1
    NOT R6, R6
    ADD R6, R6, #1
    ADD R5, R5, R6
    BRz LOOP
    BR FINISH2
FINISH1
    LEA R0, YES
    TRAP x22
    HALT
FINISH2
    LEA R0, NO
    TRAP x22
    HALT
STORE1    .FILL x303E
    .BLKW #26
STORE2    .FILL x3059
    .BLKW #26
LOAD1 .FILL x4000
LOAD2 .FILL x4001
THIRTYTWO .FILL #32
NNINETYSEVEN .FILL #-97
    .FILL YES
    .FILL NO
YES .STRINGZ "YES"
NO  .STRINGZ "NO"
    .END
```

### Pseudocode

```pseudocode
begin
in string1
in string2
n<-0
while(string1(n)!=0)then
begin
    if string1(n)==32 then continue
    else
    begin
    	if string1(n)<97 then string1(n)<-string1(n)+1
		count1(string1(n))<-count1(string1(n))+1
	end
	n<-n+1
end
n<-0
while(string2(n)!=0)then
begin
    if string2(n)==32 then continue
    else
    begin
    	if string2(n)<97 then string2(n)<-string2(n)+1
		count2(string2(n))<-count2(string1(n))+1
	end
	n<-n+1
end
for i:=97 to 122 do
	begin
	if count1(i)!=count2(i) then break
	end
end
if i == 123 then print "YES"
else print "NO"
end
```

### Problems I met

I mistakenly counted the number of English letters as 24, when the correct number should be 26, which resulted in not allocating enough space for the counter.

### Questions

1.If there are punctuation characters (such as ;:, .") in the input, how will the program handle them?

**Answer:**The program is not specifically designed to handle punctuation characters, so if there are punctuation characters in the input, the program will give incorrect output.

2.What is the format of TRAP x22 (i.e., what content is output to where)?

**Anwser:**Output from the start of address R0 until encountering a zero.