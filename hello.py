import os

if __name__ == "__main__":

    print("Hello world!")

    if not os.path.exists("./outputs"):
        os.mkdir("./outputs")
    
    with open('./outputs/hello.txt', 'w') as fp:
        fp.write("Hello world!\n")
    
    print("Goodbye!")