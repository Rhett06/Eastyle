# Master-Project
## Dataset directory
dataset1: https://drive.google.com/file/d/18xKLWtXWwH0bswrAvZw2Wq8sYiaG3Tqu/view?usp=sharing

dataset2: https://drive.google.com/file/d/1KS7jiPkw1kV48dD6SKQp-qjm6_kT5AwM/view?usp=sharing

dataset3: https://drive.google.com/file/d/1Jf42YU8IparoeQ8ab2tkd9hKnmvi6IiD/view?usp=sharing

test data: [links]
## Run this project
Run all files for dataset 1 and 3:
```
python main.py --data=[our dataset directory]
```

Run 1 violation for dataset 1 and 3:
```
python main.py --data=[our dataset directory] --rule=[violation name]
```

Run multiple rules for dataset 2:
```
python main.py --data=[our dataset directory] --rule=Multiple
```

Test 1 file in Dataset1 and 3: First create a new dataset for this file.
```
python main.py --data=[our dataset directory] --rule=[violation name]
```