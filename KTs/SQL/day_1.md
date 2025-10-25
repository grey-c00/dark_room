## RANDOM Example 1:

Consider a scenario that you have a text file (name = `random_example_1.txt`) and you need to find a word `asdf` in it. How would you find it.

One way is that you will open the file and search for this word.

Consider that your text file is of 100GB, will you be able to open that file ? I think answer will be no.

So what is the solution? 
1. maybe split that file in smaller chunks such as 5GB each and search in each file - we will need to open and search in 20 files. [Here remember the term `chunk`]
    1. How can we further optimize this?
        1. Approach 1:
            1. maybe while searching word `asdf` first time, i will have to go through all 20 files and store the file number in which `asdf` is present, in another file `random_example_1_word_asdf.txt`
            2. From any search coming onwards, I won't search in 20 files, I will search only in files that are found in `random_example_1_word_asdf.txt`
            3. Using this technique, I have reduced search space
            pros: easy to implement
            cons: <You need to answer to this question>
                1. Answer here.
                2. Answer here.
        2. Approach 2:
            1. maybe while searching word `asdf` first time, i will store line number for each file where word `asdf` is present, in another file `random_example_1_word_asdf_with_line.txt`
            2. From any search coming onwards, I won't search in 20 files, I will search only in files + lines that are found in `random_example_1_word_asdf_with_line.txt`
            3. Using this technique, I have reduced search space. This approach will do faster search then Approach1.
            pros: Fast search, faster then Approach1.
            cons: <You need to answer to this question>
                1. Answer here.
                2. Answer here.
    2. Question for you:
        1. What is RAM
        2. What is Storage
        4. How RAM is different from Storage
        5. What is bit and byte.
2. <will discuss next>

