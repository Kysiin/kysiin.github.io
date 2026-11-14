# Complexity

## Time Complexity

1. **`compareHeight` function**:

   - This function compares the heights of two rectangles. The time complexity is **O(1)**.

2. **`nextFitDecreasingHeight` function**:

   - **Sorting operation**: This function first sorts the list of rectangles in descending order by height using the standard library's `std::sort` function, which has an average time complexity of **O(n log n)**, where **n** is the number of rectangles.
   - **Arrangement operation**: After sorting, the function iterates through each rectangle to check if it can fit in the current row. If the current row cannot accommodate the new rectangle, a new row is started. This part has a time complexity of **O(n)**.

   Combining the sorting and arrangement operations, the overall time complexity of the `nextFitDecreasingHeight` function is **O(n log n)**.

3. **`generateRectangles` function**:

   - This function generates a list of rectangles with random widths and heights. The size of the list is determined by the `count` parameter. Generating each rectangle has a time complexity of **O(1)**, so the entire function's time complexity is **O(n)**, where **n** is the number of rectangles generated.

4. **`main` function**:

   - In the `main` function, the program tests different numbers of rectangles, including 10, 100, 1000, 10000, 100000, 1000000, and 10000000. For each test case, `generateRectangles` and `nextFitDecreasingHeight` are called. Since the time complexity of `nextFitDecreasingHeight` **O(n log n)** is higher than that of `generateRectangles` **O(n)**, the main time complexity is determined by the `nextFitDecreasingHeight`.

In summary, the key performance bottleneck in this code is the sorting operation in the `nextFitDecreasingHeight` function, which has a time complexity of **O(n log n)**.

## Space Complexity

1. **`compareHeight` Function**:
   - This comparison function does not use additional space, so its space complexity is **O(1)**.
2. **`nextFitDecreasingHeight` Function**:
   - This function does not require any additional data structures to store information, aside from a few variables used to track the current width, the current height of the row, and the total height. Therefore, besides the input list of rectangles, the extra space complexity is **O(1)**.
3. **`generateRectangles` Function**:
   - This function creates and returns a list of rectangles, where the size of the list directly depends on the input parameter `count`. Hence, its space complexity is **O(n)**, where **n** is the number of rectangles generated.
4. **`main` Function**:
   - In the `main` function, aside from storing the list of rectangles, an integer array `testCaseSizes` is defined to hold the sizes of different test cases. The size of the array is fixed, so it does not grow with input size, giving it a space complexity of **O(1)**. However, the primary space consumption comes from the list of rectangles, whose space complexity depends on the size of the largest test case, which is **O(n)**, where **n** is the maximum number of rectangles.

In summary, the overall space complexity of the entire code segment is primarily determined by the requirements to generate and store the list of rectangles. Although the `nextFitDecreasingHeight` function performs a sorting operation, it uses in-place sorting that does not require additional space.

Therefore, the total space complexity is mainly determined by the output of the `generateRectangles` function, which is **O(n)**, where **n** represents the number of rectangles generated.