# DBMS Normalization

## Definition

Normalization is a systematic database design technique used to organize data
in relational databases.

The main objectives of normalization are:

1. Reduce data redundancy.
2. Reduce insertion, deletion, and update anomalies.
3. Improve data consistency.
4. Organize relations using functional dependencies.

---

## Functional Dependency

A functional dependency describes a relationship between attributes.

For a relation R, a functional dependency is written as:

X → Y

It means that the value of attribute set X uniquely determines the value
of attribute set Y.

Here:

- X is called the determinant.
- Y is functionally dependent on X.

Example:

Student_ID → Student_Name

If Student_ID is known, the corresponding Student_Name can be uniquely
determined.

---

## Candidate Key

A candidate key is a minimal set of attributes that uniquely identifies
each tuple in a relation.

A relation can have multiple candidate keys.

One candidate key is selected as the primary key.

---

## Prime and Non-Prime Attributes

A prime attribute is an attribute that is part of at least one candidate key.

A non-prime attribute is an attribute that is not part of any candidate key.

---

# First Normal Form (1NF)

A relation is in First Normal Form when:

- Each attribute contains atomic values.
- There are no repeating groups.
- Each cell contains a single value.

Example of a violation:

| Student_ID | Name | Phone_Numbers |
|---|---|---|
| 1 | Rahul | 9876, 8765 |

The Phone_Numbers attribute contains multiple values.

To satisfy 1NF, the values should be represented as atomic values.

---

# Second Normal Form (2NF)

A relation is in Second Normal Form when:

1. It is already in 1NF.
2. Every non-prime attribute is fully functionally dependent on the
   whole candidate key.

2NF eliminates partial functional dependency.

Partial dependency occurs when a non-prime attribute depends on only a
proper subset of a composite candidate key.

Example:

Consider:

ENROLLMENT(Student_ID, Course_ID, Student_Name, Course_Name, Marks)

Suppose:

Student_ID → Student_Name

Course_ID → Course_Name

(Student_ID, Course_ID) → Marks

The candidate key is:

(Student_ID, Course_ID)

Student_Name depends only on Student_ID and Course_Name depends only on
Course_ID. These are partial dependencies.

Therefore, the relation is not in 2NF.

---

# Third Normal Form (3NF)

A relation is in Third Normal Form when:

1. It is in 2NF.
2. There is no transitive dependency of a non-prime attribute on a
   candidate key.

A commonly used formal condition is:

For every non-trivial functional dependency X → A, at least one of the
following should hold:

- X is a superkey, or
- A is a prime attribute.

Example:

Student_ID → Department_ID

Department_ID → Department_Name

Therefore:

Student_ID → Department_Name

Department_Name is transitively dependent on Student_ID.

This represents a transitive dependency.

---

# Boyce-Codd Normal Form (BCNF)

A relation is in BCNF if, for every non-trivial functional dependency:

X → Y

X is a superkey.

Therefore, the BCNF condition is:

Every determinant must be a superkey.

BCNF is stricter than 3NF.

A relation can be in 3NF but not in BCNF.

---

# Relationship Between Normal Forms

The commonly considered progression is:

1NF → 2NF → 3NF → BCNF

Each successive normal form imposes additional conditions on the
structure of the relation.

---

# Anomalies Reduced by Normalization

Normalization helps reduce:

## Insertion Anomaly

An insertion anomaly occurs when a new fact cannot be inserted without
also inserting unrelated information.

## Update Anomaly

An update anomaly occurs when the same information is stored in multiple
places and must be updated in several rows.

## Deletion Anomaly

A deletion anomaly occurs when deleting one piece of information
accidentally removes another important fact.

---

# Important GATE Points

- 1NF deals with atomic values.
- 2NF removes partial functional dependencies.
- 3NF removes transitive dependencies involving non-prime attributes.
- BCNF requires every determinant to be a superkey.
- Every BCNF relation is in 3NF.
- BCNF is stricter than 3NF.
- Prime attributes belong to at least one candidate key.
- Non-prime attributes belong to no candidate key.
- Functional dependencies are fundamental to normalization.