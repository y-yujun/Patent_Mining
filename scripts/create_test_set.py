from sklearn.model_selection import train_test_split

def create_test_set(input_file, output_file):
    faculty = []

    with open(input_file, 'r') as f:
        for line in f:
            if line[-1] == '\n':
                line
                faculty.append(line[:len(line)-1])
            else:
                faculty.append(line)

    _, test_set = train_test_split(faculty, test_size=0.2, random_state=50)
    
    # write the test set into a file
    with open(output_file, "w") as f:
        for item in test_set:
            f.write(str(item) + "\n")

create_test_set("faculty_namelist/lists/uiuc_faculty.txt", "test_set.txt")