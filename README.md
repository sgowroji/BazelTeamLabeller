# BazelTeamLabeller
This is the API code to predict label, where API is https://bazel-triage-bot-dot-gtech-rmi-dev.uc.r.appspot.com/predict_label?title=${encodedTitle}&description=${encodedBody} where we pass Title and Body of the newly created issue to this current api and then it predicts the team label in json format. 
{
    "team_label": "team-Android"
}
using the Github action https://github.com/sgowroji/bazel/blob/master/.github/workflows/geminilabeler.yml,  And this github action will automatically adds the team label when ever a new issue is created in the Github repository.

[Predictlabel.py](https://github.com/sgowroji/BazelTeamLabeller/blob/main/predictlabel.py) is the python code 
[Predictlabel_api.py](https://github.com/sgowroji/BazelTeamLabeller/blob/main/predictlabel_api.py) is the API code integrated with flask framework.
[Teamlabels.pdf](https://github.com/sgowroji/BazelTeamLabeller/blob/main/Teamlabels.pdf) is the current PDF which we are passing to the model, Internally it has all the team label and their description from the [maintainers guide](https://bazel.build/maintaining/maintainers-guide.html#team-labels). And programmatically we are getting 50 issues and their corresponding description from github API for all the [team labels](https://github.com/bazelbuild/bazel/labels).  using another script, Currently not adding in this repository.
