Lets take an example.

We have a table called `StudentScore` with below schema - 

- StudentId: int
- name: int
- TestId: int
- TestScore: int
- PassingMarks: int


Sample Table:

| StudentId | name          | TestId | TestScore | PassingMarks |
| --------- | ------------- | ------ | --------- | ------------ |
| 101       | Alice Johnson | M001   | 88        | 40           |
| 101       | Alice Johnson | S001   | 76        | 40           |
| 101       | Alice Johnson | E001   | 92        | 40           |
| 102       | Bob Smith     | M001   | 55        | 40           |
| 102       | Bob Smith     | S001   | 38        | 40           |
| 103       | Carol Davis   | M001   | 95        | 40           |
| 104       | Daniel Wilson | E001   | 66        | 40           |
| 104       | Daniel Wilson | S001   | 70        | 40           |
| 105       | Emily Brown   | M002   | 42        | 45           |
| 105       | Emily Brown   | E002   | 81        | 45           |



Lets imagine that at some point of time, there is updation in the name of student `Alice Johnson`. How many rows do we need to update: 3 rows. Now, imagine that we have a real big table where user `Alice Johnson` is assigned lots of tests. Then we will have to make like lots of updates into this table.

So can we reduce number of update?


## Yes, Step1:

One way is that lets break this table into two smaller table - 

First table - `Student`
- StudentId: int
- name: int

Second - `StudentScore`
- StudentId: int
- TestId: int
- TestScore: int
- PassingMarks: int

here, we can still find the name of `student` for any `studentId` in table `StudentScore` but looking up into `Student` table.


 `Student` table:

| StudentId | Name          |
| --------- | ------------- |
| 101       | Alice Johnson |
| 102       | Bob Smith     |
| 103       | Carol Davis   |
| 104       | Daniel Wilson |
| 105       | Emily Brown   |

`StudentScore` table:

| StudentId | TestId | TestScore | PassingMarks |
| --------- | ------ | --------- | ------------ |
| 101       | M001   | 88        | 40           |
| 101       | S001   | 76        | 40           |
| 101       | E001   | 92        | 40           |
| 102       | M001   | 55        | 40           |
| 102       | S001   | 38        | 40           |
| 103       | M001   | 95        | 40           |
| 104       | E001   | 66        | 40           |
| 104       | S001   | 70        | 40           |
| 105       | M002   | 42        | 45           |
| 105       | E002   | 81        | 45           |


Now, if I say that there is some change in `Alice Johnson`'s name then I just need to make one update in `Student` table. No redendent work.



Similary, there is still the similary problem. If I need to update the passing marks of TestId=`M001`. Hence, I need to make 3 updates. Can we further optimize this?

## Yes, Step2

Lets create another table `TestDetails` with columns-
- TestId
- PassingMarks

and now, `StudentScore` table will only contain-
- StudentId
- TestId
- TestScore

and other table, `Students` is as usual.

Structure will look like below:

`Students` table:
| StudentId | Name          |
| --------- | ------------- |
| 101       | Alice Johnson |
| 102       | Bob Smith     |
| 103       | Carol Davis   |
| 104       | Daniel Wilson |
| 105       | Emily Brown   |



`TestDetails` table:

| TestId | Subject | PassingMarks |
| ------ | ------- | ------------ |
| M001   | Math    | 40           |
| S001   | Science | 40           |
| E001   | English | 40           |
| M002   | Math    | 45           |
| E002   | English | 45           |



`StudentScore` table:

| StudentId | TestId | TestScore |
| --------- | ------ | --------- |
| 101       | M001   | 88        |
| 101       | S001   | 76        |
| 101       | E001   | 92        |
| 102       | M001   | 55        |
| 102       | S001   | 38        |
| 103       | M001   | 95        |
| 104       | E001   | 66        |
| 104       | S001   | 70        |
| 105       | M002   | 42        |
| 105       | E002   | 81        |


Now, if i need to make any changes around passing marks of `M001` test, then I just need to change on row.


So, we have made sure that any update (insert/delete as well) has minimal load on database. Lets get a flowchart for whatever we have done so far:

```markdown
┌──────────────────────────────────────────────┐
│              Original Table                  │
│──────────────────────────────────────────────│
│ StudentId | Name | TestId | TestScore | PassingMarks │
└──────────────────────────────────────────────┘
                     │
                     │  (Remove data redundancy — 1NF → 2NF)
                     ▼
┌────────────────────────────────┐       ┌────────────────────────────────────────────┐
│           Student              │       │           StudentTestScore                 │
│────────────────────────────────│       │────────────────────────────────────────────│
│ StudentId (PK)                 │◀─────▶│ StudentId (FK → Student.StudentId)         │
│ Name                           │       │ TestId                                     │
│                                │       │ TestScore                                  │
└────────────────────────────────┘       │ PassingMarks                               │
                                         └────────────────────────────────────────────┘
                                                         │
                                                         │ (Eliminate transitive dependency — 3NF)
                                                         ▼
                                         ┌────────────────────────────────────┐
                                         │           TestDetails              │
                                         │────────────────────────────────────│
                                         │ TestId (PK)                        │
                                         │ Subject                            │
                                         │ PassingMarks                       │
                                         └────────────────────────────────────┘




Finally:

                    ┌────────────────────────────────────┐
                    │          Student Table             │
                    │────────────────────────────────────│
                    │ StudentId (PK)                     │
                    │ Name                               │
                    └────────────────────────────────────┘
                                  │
                                  │   (1-to-many)
                                  ▼
┌──────────────────────────────────────────────────────────────┐
│                    StudentTestScore Table                    │
│──────────────────────────────────────────────────────────────│
│ StudentId (FK → Student.StudentId)                           │
│ TestId (FK → TestDetails.TestId)                             │
│ TestScore                                                    │
└──────────────────────────────────────────────────────────────┘
                                  ▲
                                  │   (many-to-one)
                                  │
                    ┌────────────────────────────────────┐
                    │          TestDetails Table          │
                    │────────────────────────────────────│
                    │ TestId (PK)                        │
                    │ Subject                            │
                    │ PassingMarks                       │
                    └────────────────────────────────────┘

```


We have 3 table, but somehow we can relate each table to any other table. This process of dividing a fat table into smaller, efficient, independet tables is knows as `normalization`


<Question> What other problems do you see with fat table?
- write here
- write here
- write here
- write here
- write here