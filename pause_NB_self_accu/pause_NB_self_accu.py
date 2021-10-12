import pandas as pd                                                               
import nltk                                                                       
import matplotlib.pyplot as plt 


# loading the raw dataset
df = pd.read_excel('SLN_PAUSE.xlsx')


def get_part(loc, feature):
     feature = feature.strip().lower()
     if feature == "word":
          part = lambda x: x.split("_")[0]
     elif feature == "pos":
          part = lambda x: x.split("_")[-1]
     else:
          raise("The second condition must be either 'word' or 'pos'.")

     return list(map(part, get_feature(loc)))


def get_feature(feature):
     try:
          return df[feature]
     except:
          msg = "\n\nPossible choices:\n To get list of word_posTag, use one of these: " \
                '["duration", "Left_first", "Right_first", "Left_second", "Right_second", "Left_third", "Right_third"].' \
                "\n\nTo get a list of words or pos tags, please add ', word' or ', pos' to the end of the above" \
                "possible choices except 'dur'."
          raise("KeyError:", feature, msg) 


def get_dataset(features):
     '''Returns a list of instances showing specified features with their pause tyes.

     args:
          features (list): a list of feature names to display. Possible choices:
               ["duration", "Left_first", "Right_first", "Left_second", "Right_second", "Left_third", "Right_third"].
               "left_first" to "right_third" will return a list of "word_posTag". If you only want words or
               pos tags at certain position (i.e., left_first..., right_third), please add ", word" or ", pos"
               to "left_first", .., "right_third". For example, "left_first, word" will get you a list of words
               that are the first left words to a target pause.

     return (list):
          the return format will be a list of tuples: [((feature1, feature2, feature3...), pause_type),...]. 
     '''
     out = []
     
     for feature in features:
          if "," not in feature:
               out.append(get_feature(feature))
          else:
               out.append(get_part(*feature.split(",")))
               
     return list(zip(zip(*out), get_feature("Pause_type")))
          

def build_featuresets(dataset, features):
     '''Convert the dataset into format suitable for training Naive Bayes model in nltk.

     Return (list):
          [(feature_dict, pause_type),...] where the feature_dict contains the feature name and the specific feature type.
     '''
     featureset = lambda x: (dict(zip(features, x[0])), x[1])
     return list(map(featureset, dataset))


# nltk.NaiveBayesClassifier also provides other convenient functions. (However, here we only care about accuracy)
# For example, to predict a label, we can use classifier.classify or classifier.classify_many;
# to get the probilities for all types of pauses, use classifier.prob_classify(a_featureset).prob(a_label),
# or use classifier.prob_classify_many(featuresets) and loop through it to get probilities for a label;
# to get the most informative features, use classifier.most_informative_features(num_to_show),
# classifier.show_most_informative_features(num_to_show). More: http://www.nltk.org/api/nltk.classify.html?highlight=naivebayesclassifier.
def accuracy(features, test_ratio, train_accu=False): 
     dataset = get_dataset(features)
     featuresets = build_featuresets(dataset, features)
     size = int(len(featuresets) * test_ratio)  
     train_set, test_set = featuresets[size:], featuresets[:size]  
     classifier = nltk.NaiveBayesClassifier.train(train_set)
     if not train_accu:
          return nltk.classify.accuracy(classifier, test_set)
     else:
          return nltk.classify.accuracy(classifier, train_set)


# These conditions mimic the rules used for building this Unfilled Pause Classifier where
# the frist two words and pos tags are heavily employed, the third words (left & right)
# and pos tags are occasionally used and the duration is never used. Therefore, comparing cond1
# and cond2, you will find that "duration" only have tiny effects in the self-predicting accuracy.
# Similarly, if we only use the last two words/tags or only one of them, the accuracy will descrease drastically.
# Generally, the more complex a condition is, the closer it is to the classifying rules I used, although these
# condition may not have the best test set accuracy (e.g., cond1 and cond2, but they have the best train set accuracy) .
cond1 = ["duration", "Left_first", "Right_first", "Left_second", "Right_second", "Left_third", "Right_third"]
cond2 = ["Left_first", "Right_first", "Left_second", "Right_second", "Left_third", "Right_third"]
cond3 = ["Left_first", "Right_first", "Left_second", "Right_second"]
cond4 = ["Left_first", "Right_first"]
cond5 = ["Left_first, word", "Right_first, word", "Left_second, word", "Right_second, word"]
cond6 = ["Right_first, pos", "Left_first, pos", "Left_second, pos", "Right_second, pos"]
cond7 = ["Left_first, word", "Right_first, pos", "Left_second, pos", "Right_second, word"]
conditions = {"cond1": cond1, "cond2": cond2, "cond3": cond3, "cond4": cond4,
              "cond5": cond5, "cond6": cond6, "cond7": cond7}


def main(train_accu=False):
     '''Save the plot of the train/test set self-predicting accuracy.

     args:
          train_accu (bool): defaults to False. When set True, the train set
          self-predicting accuracy will be plotted and saved.
     '''
     if not train_accu:
          test_ratios = [0.1, 0.2, 0.3, 0.4, 0.5]
          ratios = test_ratios
          label = "test"
     else:
          test_ratios = [0, 0.1, 0.2, 0.3, 0.4]
          ratios = [1, 0.9, 0.8, 0.7, 0.6]
          label = "train" 
     
     # plotting
     figure = plt.figure()
     for k, v in conditions.items():
          accu = []
          for test_ratio in test_ratios:
               accu.append(accuracy(v, test_ratio, train_accu))
          plt.plot(ratios, accu, label=k)

     plt.legend(bbox_to_anchor=(1.01, 1), loc='upper left')
     plt.title("Self-predicting accuracy using Naive Bayes models under different conditions", fontsize=8)
     plt.xlabel(f"{label.capitalize()} set ratio", fontsize=8)
     plt.ylabel("Accuracy", fontsize=8)

     # save the plot
     plt.savefig(f'naive_bayes_self_pred_accu_{label}.png', dpi=300, bbox_inches='tight', pad_inches=1)

     # print/save the conditions for current/later loop-up
     f = open("conditions.txt", "w")
     for k, v in conditions.items():
          print(k, v)
          f.write(k + "\t" + str(v) + "\n")

     f.close()

     # finally, let the plot shown
     plt.show()


if __name__ == "__main__":
     main()
