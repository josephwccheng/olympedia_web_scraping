import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer

# feature importance
import eli5

# performance metrics
from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc, matthews_corrcoef

# models
import xgboost as xgb

# plotting
import matplotlib.pyplot as plt

"""
Main Objective:
    - Create three models to predict the probability of an athelete winning a medal "Medal Count"
        - All Feature Columns 
        - Filter "Sport" to "Aquatics"
        - Filter "Event" to "Slalom" and "Giant Slalom"

1. Read CSV File
2. Data exploration
    2.1. Main Feature Column
        1. "Prior Games Bin Competitor Event Finishing Position " - categorical value - {'4-10', 'Did Not Compete', '11-20', 'Top 3', '21-30', '30+'}
            - Athele's Event Rank result from prior Olympic Game and binned into catorigies above
        2. "Age (yrs) Feature" - numeric
            - Derived from source "AGE" and filling in missing values with average age from the specific sport
        3. "Height cm Feature" - numeric
            - Derived from source "Height" and filling in missing values with average age from the specific sport
        4. "Weight kg Feature" - numeric
            - Derived from source "Weight" and filling in missing values with average age from the specific sport
        5. "BMI" - numeric
            - Derived from Height and Weight
        6. "Prior Games Country Medals per Competitor" - numeric
            - Derived from aggregrate of sport and country games a count of medals / a count of competitors
        7. "Gender" - categorical value - {'women', 'men'}
            - Derived from source data
        8. "Sport" - categorical value - {'Gymnastics', 'Aquatics', 'Skiing', 'Biathlon', 'Shooting', 'Athletics'}
            - Derived from source data
        9. "Prior Games Country Event Medals per Competitor" - numeric
            - Total number of medal won / Number of Competitor that competed for the country in prior Olympic Game
        10. "Prior Games Best Result Country Event" - numeric
            - For the country, what was the best result for that event in prior Olympic Game
        11. "Prior Games Avg Result Country Sport" - numeric
            - For the country, what was the average result for that event in prior Olympic Game
        12. "No of Outside OG Medal References" - numeric
            - # of medals for the athele of medals won outside of the olympics
        13. "Country Low Cardinality"  - categorical value - {'Austria', 'Croatia', 'Cuba', 'Hungary', 'France', 'People&#39;s Republic of China', 'Australia', 'Kenya', 'Germany', 'Great Britain', 'Sweden', 'Jamaica', 'Czech Republic', 'Russian Federation', 'Canada', 'Ukraine', 'Norway', 'Not in Top 25 Countries', 'ROC', 'United States', 'Italy', 'Ethiopia', 'Japan', 'Belarus', 'Poland', 'Switzerland'}
            - # reserving top 25 countries Olympics medal count and labelling the remaining as 'Not in Top 25 Countries'
        14. "Event" - categorical value - {'Giant Slalom', 'Skeet', '1,500 metres', '200 metres Breaststroke', 'Small-Bore Rifle, Three Positions, 50 metres', '200 metres Individual Medley', 'Pole Vault', 'Ski Cross', '100 metres Hurdles', 'Rapid-Fire Pistol, 25 metres', '7.5 kilometres Sprint', '12.5 kilometres Pursuit', 'Super G', '10 kilometres Sprint', 'Downhill', 'High Jump', '10,000 metres', 'Air Rifle, 10 metres, Team', 'Small-Bore Rifle, Prone, 50 metres', 'Free Pistol, 50 metres', '200 metres Freestyle', 'Trap', 'Slalom', 'Double Trap', '12.5 kilometres Mass Start', 'Aerials', '400 metres Hurdles', 'Air Rifle, 10 metres', '400 metres', '50 metres Freestyle', '800 metres Freestyle', '800 metres', 'Moguls', '100 metres Breaststroke', '200 metres Backstroke', 'Air Pistol, 10 metres, Team', '100 metres Backstroke', '200 metres Butterfly', '50 kilometres Walk', '15 kilometres Mass Start', '400 metres Freestyle', 'Halfpipe', '10 kilometres Pursuit', '200 metres', 'Air Pistol, 10 metres', 'Discus Throw', '110 metres Hurdles', 'Heptathlon', '400 metres Individual Medley', '1,500 metres Freestyle', 'Individual', '15 kilometres', '100 metres', 'Slopestyle', 'Alpine Combined', 'Long Jump', '20 kilometres', 'Super Combined', 'Triple Jump', 'Decathlon', '100 metres Freestyle', 'Hammer Throw', 'Marathon', '20 kilometres Walk', '3,000 metres Steeplechase', 'Sporting Pistol, 25 metres', '5,000 metres', '100 metres Butterfly', 'Javelin Throw', 'Shot Put'}
            - # Derived from source
        15. "Prior Games Competitor Event Finishing Position" - numeric
            - derived from source data and aggregating prior year's position
            - # Note: Might have coliniearity issues with "Prior Games Bin Competitor Event Finishing Position "
        16. "Host Country Competitor" - numeric
            - Home court advantage
    2.2. Prediction Column
        - "Medal Count" - categorical value - {0,1}
    2.3. Additional Features
        - "Discipline" - categorical value - {'Swimming', 'Alpine Skiing', 'Biathlon', 'Rhythmic Gymnastics', 'Athletics', 'Shooting', 'Freestyle Skiing'}
        - "Season" 
    2.4. (Out of Scope)
        - "Event Result Rank" - numeric

3. Splitting Test and Train Split
    - Using "Train_Test_Split_2020_2018" columns

4. Filter out the Main Feature Columns into a single dataframe

5. Data preprocessing
    - Categorical Data
    - Normalising Numeric data
6. Train Model

7. Obtain Results
"""

# <Data Exploratory Function>
# Print out all unique values from dataframe where data type is detected as Object
def unique_values_from_object_columns(df, max_result_length = 30):
    headers = df.dtypes.to_dict()
    # print('Listing unique values for categorical data from source data')
    for key in headers:
        if(headers[key].str== '|O'):
            unique_values = set(df[key].to_list())
            # print(f'{key} : {",".join([str(value) for value in unique_values][:max_result_length])}')

# <Performance Evaluation function>
def plot_roc_curve(fpr, tpr, label=None):
    """
    The ROC curve, modified from 
    Hands-On Machine learning with Scikit-Learn and TensorFlow; p.91
    """
    plt.figure(figsize=(8,8))
    plt.title('ROC Curve')
    plt.plot(fpr, tpr, linewidth=2, label=label)
    plt.plot([0, 1], [0, 1], 'k--')
    plt.axis([-0.005, 1, 0, 1.005])
    plt.xticks(np.arange(0,1, 0.05), rotation=90)
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate (Recall)")
    plt.legend(loc='best')
    plt.show()

if __name__ == "__main__":
    # 1. Reading in CSV File
    raw_olympic_data_file_path = "./tableau_challenge/Tableau Prep Olympics Data Output.csv"
    raw_olympic_data_df = pd.read_csv(raw_olympic_data_file_path)
    
    # <IMPORTANT> - filter data for slalom event only
    raw_olympic_data_df = raw_olympic_data_df[(raw_olympic_data_df['Event'] == 'Slalom') | (raw_olympic_data_df['Event'] == 'Giant Slalom')]
    
    # 2. Data Exploratory
    unique_values_from_object_columns(raw_olympic_data_df)

    # 3. Splitting Test and Train Data
    raw_train_data_df = raw_olympic_data_df[raw_olympic_data_df['Train_Test_Split_2020_2018'] == 'train']
    raw_test_data_df = raw_olympic_data_df[raw_olympic_data_df['Train_Test_Split_2020_2018'] == 'test']

    print(f'Row count - train: {len(raw_train_data_df.index)} - test: {len(raw_test_data_df.index)} - total: {len(raw_olympic_data_df.index)}')

    # 4. Filter out the Main Feature Columns into a single dataframe
    feature_columns = ["Prior Games Bin Competitor Event Finishing Position ", "Age (yrs) Feature", "Height cm Feature", "Weight kg Feature", "BMI", "Prior Games Country Medals per Competitor", "Gender", "Sport", "Prior Games Country Event Medals per Competitor","Prior Games Best Result Country Event", "Prior Games Avg Result Country Sport", "No of Outside OG Medal References", "Country Low Cardinality",  "Event", "Prior Games Competitor Event Finishing Position", "Host Country Competitor"]
    output_column = ["Medal Count"]
    
    X_train_df = raw_train_data_df[feature_columns]
    y_train_df = raw_train_data_df[output_column]

    X_test_df = raw_test_data_df[feature_columns]
    y_test_df = raw_test_data_df[output_column]

    # 4.1. Data Processing
    # Note: Categorical columns: ['Prior Games Bin Competitor Event Finishing Position ', 'Gender', 'Sport', 'Country Low Cardinality', 'Event']
    
    # Identify numeric_features and categorical features
    # One Hot Encoding to encode categorical values

    numeric_features = X_train_df.select_dtypes(include=['int64', 'float64']).columns
    categorical_features = X_train_df.select_dtypes(include=['object', 'category', 'period[M]']).columns

    print(f'Numeric Features are: {list(numeric_features)}')
    print(f'Categorical Features are: {list(categorical_features)}')

    # create a transformer for the categorical values
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
        ('one_hot', OneHotEncoder(handle_unknown='ignore', sparse=False))])

    # create a transformed for the numerical values
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())])


    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])

    '''XGBOOST MODEL
    Hyper parameter tuning
        Fix learning rate and number of estimators for tuning tree-based parameters
        max_depth = 5 : This should be between 3-10. I’ve started with 5 but you can choose a different number as well. 4-6 can be good starting points.
        min_child_weight = 1 : A smaller value is chosen because it is a highly imbalanced class problem and leaf nodes can have smaller size groups.
        gamma = 0 : A smaller value like 0.1-0.2 can also be chosen for starting. This will anyways be tuned later.
        subsample, colsample_bytree = 0.8 : This is a commonly used used start value. Typical values range between 0.5-0.9.
        scale_pos_weight = 1: Because of high class imbalance.
    '''

    clf = Pipeline(steps=[('preprocessor', preprocessor),
                        ('classifier', xgb.XGBClassifier(
                            objective= 'binary:logistic',
                            learning_rate =0.05,
                            n_estimators=1000,
                            min_child_weight = 1,
                            max_depth=5,
                        ))])

    # Model Training
    clf.fit(X_train_df, y_train_df.values.ravel())

    # Model Scoring
    clf.score(X_test_df, y_test_df.values.ravel())


    # Feature Importance in Pipelines
    # Obtaining the list of one hot encoded columns from preprocessor step -> catorical transformer cat -> and get the OneHotEncoder one_hot
    onehot_columns = list(clf.named_steps['preprocessor']
                                .named_transformers_['cat']
                                    .named_steps['one_hot'].get_feature_names(input_features=categorical_features)
                        )

    # Join the onehot columns with numerical columns
    all_feature_columns = list(numeric_features)
    all_feature_columns.extend(onehot_columns)

    feature_importance = eli5.explain_weights(clf.named_steps['classifier'], top=50, feature_names=all_feature_columns)
    # feature_importance = eli5.explain_weights(clf.named_steps['classifier'], top=50, feature_names=all_feature_columns, feature_filter=lambda x: x != '<BIAS>')
    explain_weights = eli5.format_as_text(feature_importance)
    print(explain_weights)


    # Performance metrics
    # AUC - The Area Under the Curve (AUC) represents the rate of correct classification by a logistic model. An AUC of 0.5 means that the model performs no better than random guessing. An AUC of 1.0 means that the model correctly classifies data 100% of the time, which can indicate data leakage.
    y_pred =  clf.predict(X_test_df)
    y_test = y_test_df.values.ravel()
    fpr, tpr, thresholds = roc_curve(y_test, y_pred, pos_label=1)
    AUC_score = auc(fpr, tpr)
    print(f'AUC score is {AUC_score}')
    # plotting ROC curve
    plot_roc_curve(fpr, tpr, 'testing')

    # MCC - The Matthews Correlation Coefficient (MCC) measures the quality of this logistic model. MCC provides a more even representation of the four parts of the confusion matrix than other classification metrics.
    MCC_score = matthews_corrcoef(y_test, y_pred)
    print(f'MCC score is {MCC_score}')

    # Confusion Matrix
    print(f'Confusion Matrix : {confusion_matrix(y_test, y_pred, labels = [1,0])}')


    print("Classification Report")
    print(classification_report(y_test, y_pred))

    print('debug')