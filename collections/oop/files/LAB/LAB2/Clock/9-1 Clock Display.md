# 9-1 Clock Display

Write a class `NumberDisplay` that expresses a counter with at least the following interface:

```c++
class NumberDisplay {

public.

NumberDisplay(int limit); // create a number display with a given up-limit

void setValue(int value); // set the value

int getValue(); // get the value

std::string toString(); // get a string description of the value, with leading 0 for value less than 10

bool dida(); // increase the value by one, turn over to zero if the value reaches the limit, returns true if the value turned to zero

}
```

The internal value should be zero when an object is created.
Write a class `Clock` that expresses a clock with hours, minutes, and seconds, using `NumberDisplay` to represent the internal data, with at least the following interface:

```c++
class Clock {

public.

Clock(int hour, int minute, int second); // create a clock with given time

std::string toString(); // get a string description of "hh:mm:ss"

void dida(); // run a second

}
```

A main.cpp is provided, which contains `main()` for testing. The two classes you have written (or other required code) need to be placed in the `src` directory.
The name of the header file and the name of the class have been specified in the main.cpp for testing; do not change these two names.

A Makefile has been provided in the `src` directory, which will compile the code files mentioned by OBJS and integrate the library file clock.a.

The current Makefile specifies two files, numberdisplay.o and clock.o, which you can modify or add to your own source files. Because clock.a is a Unix library file, on Windows, you need to use WSL to compile it.