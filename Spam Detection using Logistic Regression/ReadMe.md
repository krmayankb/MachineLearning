# Spam Detection using Logistics Regression

This notebook explains all the steps involved in Logistics Regression modelling for Spam Detection.

### **Pre-processing:**
1. Remove numbers
2. Replace multiple whitespaces with single white spaces.
3. Tokenize the data: Used nltk library function to tokenize the email data. This is very first step towards
preprocessing and mandatory for easily performing next steps in pre-processing the data.
4. Remove stopwords: These are frequently used words and removing these helps with allowing the model to focus on other important attributes in the dataset.
5. Remove punctuation 
6. Find Stem
7. Lemmatize the tokens 

  - Observation: lemmatization after stemming did not improve the results. Stemming had better results, hence stemming was prefered.

8. Calculate TFIDF and count vectors: TFIDF had better results in comparison to count. So, we decided to move with TFIDF vector.This also make sense 
logically as TFIDF vector has more information i.e., combination of TF and IDF.


### Training
1. Weighted logistics regression (in inverse ratio to class label distribution)
2. Grid Search: I applied grid search to optimize on the three major parameters:
  a. Penalty – to select between l1 and l2.
  b. C – to get optimal value of regularization coefficient with the penalty chosen.
  c. Weights – I started with actual inverse weight ratio of spam to non-spam and performed grid search to get optimal value of the weight in 
  combination with penalty and C.

### Parameters of evaluation:
1. Recall
2. Precision
3. F1 Score
4. Accuracy


### Libraries: 
ntlk, scikit-learn, pandas, matplotlib, NumPy

### Kaggle competition link
https://www.kaggle.com/c/spam-classification-ee-p-596 
