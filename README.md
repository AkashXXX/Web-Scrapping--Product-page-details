The code was used to scrape the product image, product title, discount, and selling price from the product page whose URL is given, along with some other product details. The output contains the product image and a prompt column that will be used for generating banner ads for that particular product. The output generated work as an input for the chatgpt api to generate an image for each product.

Note: Here I used selenium to scrape the data because the product image URL was not present in the raw HTML but was being fetched by some api or a JavaScript code. Another challenge was to give a pause after each row while running the code, otherwise it won't fetch and give a blank output.

For better understanding, an input and output file is also attached in this repository.
