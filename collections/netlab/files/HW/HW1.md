## 1.
What is the name of PDU at the network layer of the OSI reference model?
A. message
B. frame
C. packet
D. segment
>**C**
## 2.
 Connectionless Services is also called
 A. virtual circuit service
B. acknowledged datagram service
C. client-server service
D. datagram service
>**D**
---
## 3.
 Which of the OSI layers handlers each of the following:
(a) Dividing the transmitted bit stream into frames.
>**Data Link Layer**

(b) Determining which route through the subnet to use.
>**Network Layer**

## 4.
A system has an 7-layer protocol hierarchy. Applications generate messages of length 1000 bytes. At each of the layers, an 20 byte header is added. What fraction of the network bandwidth is filled with headers? (round to one decimal place)

>$$
>\frac{7 \times 20}{1000+7\times20} \approx 12.3\%
>$$

## 5.
 How long was a bit on the original 802.3 standard in meters? Use a transmission speed of 10 Mbps and assume the propagation speed in coax is 2/3 the speed of light in vacuum. (round to one decimal place)

>$$
>v = \frac{2}{3} \times 3 \times 10^8 = 2 \times 10^8 \text{ m/s}\\
>t_{\text{bit}} = \frac{1}{10 \times 10^6} = 10^{-7} \text{ s} = 0.1 \ \mu\text{s}\\
>\text{Length} = v \times t_{\text{bit}} = (2 \times 10^8) \times (10^{-7})\\
>= 2 \times 10^{1} = 20 \text{ m}\\
>$$
## 6.
 A client-server system uses a satellite network, with the satellite at a height of
40000 km. What is the best-case delay in response to a request? (round to one decimal place)

>$$
>Total\ distance = 4 \times 40000 km = 160000 km \\
>c=3 \times 10^8 m/s = 300,000 km/s \\
>Delay = \frac{Total \ distance}{c}=0.5333...s \approx 0.5s
>$$

## 7.
An image is 1024 x 768 pixels with 3 bytes/pixel. Assume the image is uncompressed. (round to one decimal place)
>$$
>Total \ Bits = 1024 \times 768 \times 3 = 18,874,368 \\
>T = \frac{Total \ Bits}{Bandwidth}
>$$

(a) How long does it take to transmit it over a 56-kbps modem channel?
>$$
>T \approx 337.0s
>$$

(b) How long does it take to transmit it over a 1-Mbps cable modem?
>$$
>T \approx 18.9s
>$$

(c) How long does it take to transmit it over a 10-Mbps Ethernet?
>$$
>T \approx 1.9s
>$$

(d) How long does it take to transmit it over 100-Mbps Ethernet?
>$$
>T \approx 0.2s
>$$

## 8.
A collection of five routers is to be connected in a point-to-point subnet. Between each pair of routers, the designers may put a high-speed line, a medium-speed line, a low-speed line, or no line. If it takes 100ms of computer time to generate and inspect each topology, how long will it take to inspect all of them? (round to one decimal place)
>$$
>\binom{5}{2} = \frac{5 \times 4}{2} = 10 \text{ pairs} \\
>4^{10} = 1{,}048{,}576 \\
>\text{Total time} = 1{,}048{,}576 \times 0.1 \text{ s} \\
>= 104{,}857.6 \text{ s}
>$$
