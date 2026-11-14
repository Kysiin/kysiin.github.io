# LAB3 REPORT

### Pseudocode

```pseudocode
begin
	in string1
	n<-0
	i<-50
	j<-49
	while string1(n)!=0 do
		if string1(n)=='+' then
		begin
			n<-n+1
			i<-i-1
			string2(i)<-string1(n)
		end
		if string1(n)=='-' then
		begin
			output string2(i)
			string2(i)<-0
			i<-i+1
		end
		if string1(n)=='[' then
		begin
			n<-n+1
			j<-j+1
			string2(j)<-string1(n)
		end
		if string1(n)==']' then
		begin
			output string2(j)
			string2(j)<-0
			j<-j-1
		end
		n<-n+1
	end

end
```

### Questions

**Premise**: The stack pointed by my head and tail pointers will not be an empty stack.

#### Question 1: There are a total of 6000 instructions. If the stack can hold a maximum of 1000 elements, how large does this stack need to be? Is 1000 slots enough?

In extreme cases, the required stack size can be larger than 1000 slots, as the spaces left behind after elements are removed from the stack cannot be reused, resulting in the need for a stack much larger than 1000 slots.

#### If only 1000 slots are available, how can we store these elements?

We can create a circular stack by connecting the head and tail of the stack. When the tail pointer reaches the 1000th slot, it wraps around to the first slot. Since there can be a maximum of 1000 elements in the stack at the same time, there will always be empty spaces at the head.

#### In this situation, what will be the relationship between R (tail pointer) and L (head pointer) after all 1000 elements have been read in?

L = R + 1.Before any data is read, the relationship between L and R is L = R + 1, and it remains the same after the process is complete.

### Problems I met

After the pop operation, I forgot to reset the stack to zero, which caused the symbol ']' to output elements that had already been output by '-'.