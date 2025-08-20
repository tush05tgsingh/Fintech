### book used:
1) ![fraud detection handbook](https://fraud-detection-handbook.github.io/fraud-detection-handbook/Chapter_2_Background/MachineLearningForFraudDetection.html)

2) ![]

#### Overview of challenges in Credit Card Fraud Detection:

1) Class Imbalance: credit fraud transaction could by 1% of the entire transaction 
2) Concept Drift : Patterns change and we need to keep up with different spending habits, transaction types etc
3) Near real-time requirements: parallelization is important 
4) Categorical features: ML doesnt handle categories well. These can be handled by feature aggregation, graph-based transformation, deep-learning appraches 
5) Sequential modeling: data is like a stream, need to understand it to detect abnormal behavior by aggreagting features or using models like hidden markov model or RNN 
6) Class overlap : raw information is difficult to track hence feature engineering is important
7) Performance measures: Standard measures for classification systems, such as the mean misclassification error or the AUC ROC, are not well suited for detection problems due to the class imbalance issue
8) Lack of public datasets: Very few public datasets to actually train on.