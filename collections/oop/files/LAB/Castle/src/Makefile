CC = g++
CFLAG = -std=c++11 -Wall
OBJS = Room.o NormalRoom.o MonsterRoom.o PrincessRoom.o Castle.o main.o
TARGET = castle

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAG) -o $(TARGET) $(OBJS)

%.o: %.cpp
	$(CC) $(CFLAG) -c $< -o $@

clean:
	rm -f $(OBJS) $(TARGET)
