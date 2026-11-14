# LAB6 REPORT

## Pseudocode

```pseudocode
begin:
int BtoD(char *p);			//binary to decimal
void DtoB(int d,char *r);	//Decimal to Binary
int offset6(char *p);
int offset9(char *p);
int offset11(char *p);		//calculate offset6/9/11
int mem[70000]={0x7777}; 	//memory initialized to 0x7777
int R[8]={0x7777};			//register initialized to 0x7777
in pc;						//The first line is the starting address of the program
char binary[16];			//read binary code
int backuppc=pc;			//save original pc
int nzp=2;					//nzp=010
int opcode=0;
while(in binary!=EOF){
	mem[pc]=BtoD(binary);	//write code into memory
	pc++;
}
pc=backuppc;				//reset pc
for(;pc<70000;pc++){
	opcode=mem[pc]/16/16/16	//the front four of the current line
	if(opcode==15) then break;//HALT
	int DR=binary[9]+binary[10]*2+binary[11]*4;
        int SR1=binary[6]+binary[7]*2+binary[8]*4;
        int SR2=binary[0]+binary[1]*2+binary[2]*4;
        char imm5[16]={binary[0],binary[1],binary[2],binary[3],binary[4],binary[4],binary[4],binary[4],binary[4],binary[4],binary[4],binary[4],binary[4],binary[4],binary[4],binary[4]};	//binary imm5 extension
	switch(opcode){
		case 0://BR
		if((nzp==1&&binary[9]) || (nzp==2&&binary[10]) || (nzp==4&&binary[11])){
                    pc+=offset9(binary);//pc=pc+offset9
                }
        break;
        case 1://ADD
//if (bit[5] == 0)
//DR = SR1 + SR2;
//else
//DR = SR1 + SEXT(imm5);
//setcc()
            DtoB(R[SR1],a);				//R[SR1]and[SR2] to binary so that it could be added in binary
            DtoB(R[SR2],b);
            if(binary[5]==0){
                R[DR]=0;
                for(int i=15;i>=0;i--){
                    R[DR]=R[DR]*2+a[i]+b[i];	//add in binary
                }
            }else{
                R[DR]=0;
                for(int i=15;i>=0;i--){
                    R[DR]=R[DR]*2+a[i]+imm5[i];	//add in binary
                }
            }
            if(R[DR]>0xFFFF){
                R[DR]=R[DR]-0x10000;
            }
            DtoB(R[DR],tmp);
            if(R[DR]==0) {				// set cc
                nzp=2;//0x010
            }else if(tmp[15]==1){
                nzp=4;//0x100
            }else{
                nzp=1;//0x001
            }
            break;
        case 2://LD
//if (computed address is in privileged memory AND PSR[15] == 1)
//Initiate ACV exception;
//else
//DR = mem[PC† + SEXT(PCoffset9)];
//setcc();
            R[DR]=mem[pc+1+offset9(binary)];
            DtoB(R[DR],tmp);
            if(R[DR]==0) {
                nzp=2;//0x010
            }else if(tmp[15]==1){
                nzp=4;//0x100
            }else{
                nzp=1;//0x001
            }
            break;
        case 3://ST
            mem[pc+1+offset9(binary)]=R[DR];
            break;
        case 4://JSR
            R[7]=pc+1;
            if(binary[11]==0){
                pc=R[SR1]-1;
            }else{
                pc=pc+offset11(binary);
            }
            break;
        case 5://AND
            DtoB(R[SR1],a);
            DtoB(R[SR2],b);
            R[DR]=0;
            if(binary[5]==0){
                for(int i=15;i>=0;i--){
                    if(b[i]==0){
                        a[i]=0;
                    }
                    R[DR]=2*R[DR]+a[i];
                }

            }else{
                R[DR]=0;
                for(int i=15;i>=0;i--){
                    if(imm5[i]==0){
                        a[i]=0;
                    }
                    R[DR]=2*R[DR]+a[i];
                }
            }
            DtoB(R[DR],tmp);
            if(R[DR]==0) {
                nzp=2;//0x010
            }else if(tmp[15]==1){
                nzp=4;//0x100
            }else{
                nzp=1;//0x001
            }
            break;
        case 6://LDR
            R[DR]=mem[R[SR1]+offset6(binary)];
            DtoB(R[DR],tmp);
            if(R[DR]==0) {
                nzp=2;//0x010
            }else if(tmp[15]==1){
                nzp=4;//0x100
            }else{
                nzp=1;//0x001
            }
            break;
        case 7://STR
            mem[R[SR1]+offset6(binary)]=R[DR];
            break;
        case 9://NOT
            DtoB(R[SR1],tmp);
            for(int i=0;i<16;i++){
                tmp[i]=1-tmp[i];
            }
            R[DR]=0;
            for(int i=15;i>=0;i--){
                R[DR]=R[DR]*2+tmp[i];
            };
            DtoB(R[DR],tmp);
            if(R[DR]==0) {
                nzp=2;//0x010
            }else if(tmp[15]==1){
                nzp=4;//0x100
            }else{
                nzp=1;//0x001
            }
            break;
        case 10://LDI
            R[DR]=mem[mem[pc+1+offset9(binary)]];
            DtoB(R[DR],tmp);
            if(R[DR]==0) {
                nzp=2;//0x010
            }else if(tmp[15]==1){
                nzp=4;//0x100
            }else{
                nzp=1;//0x001
            }
            break;
        case 11://STI
            mem[mem[pc+1+offset9(binary)]]=R[DR];
            break;
        case 12://JMP
            pc=R[SR1]-1;
            break;
        case 14://LEA
            R[DR]=pc+1+offset9(binary);
            break;
        }
    }
    for(int i=0;i<8;i++){
            printf("R%d = x%04X\n",i,R[i]);
    }
    return 0;
}
int BtoD(char *p){
    int a=0;
    int k=1;
    for(int i=15;i>=0;i--){
        a+=(p[i]-48)*k;			//'-48' because it's a character
        k=k*2;
    }
    return a;
}
void DtoB(int d,char *r){
    for(int i=0;i<16;i++){
        r[i]=d%2;
        d=d/2;
    }
}
int offset9(char *p)
{
    int a=0;
    int k=1;
    if(p[8]==0){
        for(int i=0;i<8;i++){
            a+=p[i]*k;
            k=k*2;
        }
    }else{							// if negative
        char b[9];
        for(int i=0;i<9;i++){
            if(p[i]==0)    b[i]=1;
            if(p[i]==1)    b[i]=0;
        }
        for(int i=0;i<8;i++){
            a+=b[i]*k;
            k=k*2;
        }
        a=-(a+1);					//negate and add one
    }
    return a;
}
int offset6(char *p)
{
    int a=0;
    int k=1;
    if(p[5]==0){
        for(int i=0;i<5;i++){
            a+=p[i]*k;
            k=k*2;
        }
    }else{
        char b[6];
        for(int i=0;i<6;i++){
            if(p[i]==0)    b[i]=1;
            if(p[i]==1)    b[i]=0;
        }
        for(int i=0;i<5;i++){
            a+=b[i]*k;
            k=k*2;
        }
        a=-(a+1);
    }
    return a;
}
int offset11(char *p)
{
    int a=0;
    int k=1;
    if(p[10]==0){
        for(int i=0;i<10;i++){
            a+=p[i]*k;
            k=k*2;
        }
    }else{
        char b[11];
        for(int i=0;i<11;i++){
            if(p[i]==0)    b[i]=1;
            if(p[i]==1)    b[i]=0;
        }
        for(int i=0;i<10;i++){
            a+=b[i]*k;
            k=k*2;
        }
        a=-(a+1);
    }
    return a;
}
end
```

## Errors

At first, I used decimal addition and subtraction directly. Since an int has 32 bits while the Register only has 16 bits, it would result in negative numbers being treated as positive. So, I decided to switch everything to binary addition and subtraction(though it took me loads of time to correct errors in converting and binary calculation).

And it end up well:)
