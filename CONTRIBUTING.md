# Contributing to protocol-assurance

\[adapted from the [Pydra contribution guide](https://github.com/nipype/pydra/blob/master/CONTRIBUTING.md)\]

Welcome to the _protocol-assurance_ repository! We're excited you're here and want to contribute.

These guidelines are designed to make it as easy as possible to get involved.
If you have any questions that aren't discussed below, please let us know by opening an [issue][link_doc_issues]!

Before you start you'll need to set up a free GitHub account and sign in, here are some [instructions][link_signupinstructions].
If you are not familiar with version control systems such as git,
introductions and tutorials may be found [here](http://www.reproducibleimaging.org/module-reproducible-basics/02-vcs/).

## Acknowledgements

If you contribute any modifications to the code please remember to add yourself
to the authors list in the `pyproject.toml`.

## How can you contribute

There are two main ways of contributing to the project:

**1. Provide suggestions, comments and report problems**

If you want to share anything with the community and developers, please open [a new issue][link_new_issues].
There are multiple templates that you can choose from, please fill them out to the best of your ability.
- **Bug report** - report if something is not working correctly or the documentation is incorrect
- **Documentation improvement** - request improvements to the documentation and tutorials
- **Feature request** - share an idea for a new feature, or changes to an existing feature
- **Maintenance and Delivery** - suggest changes to development infrastructure, testing, and delivery
- **Questions** - ask questions regarding the tool and the usage


**2. Improve the code and documentation**

We appreciate all improvement to the _protocol-assurance_ code or documentation.
Please try to follow the recommended steps, and don't hesitate to ask questions!


**i. Comment on an existing issue or open a new issue describing your idea**

This allows other members of the _protocol-assurance_ development team to confirm
that you aren't overlapping with work that's currently underway and
that everyone is on the same page with the goal of the work you're going to carry out.

**ii. [Branch][link_branch] the [protocol_assurance repository](https://github.com/Australian-Epilepsy-Project/protocol_assurance) the repository**

This creates a copy of the repository which you can work on without affecting anyone else's work,
so it's a safe space to explore edits to the code!

**iii. Install protocol-assurance on your machine**

To install your version of _protocol-assurance_, and the dependencies needed for development,
in your Python environment (Python 3.7 or higher), run `python3 -m pip install -e ".[dev,test]"`
from your local _protocol-assurance_ directory.
Alternatively, one can develop the code using the docker image.

In order to check if everything is working correctly, run the tests
using [pytest](https://docs.pytest.org/en/latest/), e.g. `pytest -vs`, from the source directory.

**iv. Install pre-commit.**

[pre-commit](https://pre-commit.com/) is a git hook for running operations at commit time.
To use it in your environment, do `python3 -m pip install pre-commit` followed by `pre-commit install`
inside your source directory.


**v. Make the changes you've discussed.**

It's a good practice to create [a new branch](https://help.github.com/articles/about-branches/)
of the repository for a new set of changes.
Once you start working on your changes, test frequently to ensure you are not breaking the existing code.
It's also a good idea to [commit][link_commit] your changes whenever
you finish specific task, and [push][link_push] your work to your GitHub repository.


**vi. Submit a [pull request][link_pullrequest].**

A new pull request for your changes should be created from your branch or fork of the repository
after you push all the changes you made on your local machine. This pull request should made onto the `dev` branch.

When opening a pull request, please use one of the following prefixes:


* **[ENH]** for enhancements
* **[FIX]** for bug fixes
* **[MNT]** for maintenance
* **[TST]** for new or updated tests
* **[DOC]** for new or updated documentation
* **[STY]** for stylistic changes
* **[REF]** for refactoring existing code


**Pull requests should be submitted early and often (please don't mix too many unrelated changes within one PR)!**
If your pull request is not yet ready to be merged, please also include the **[WIP]** prefix (you can remove it once your PR is ready to be merged).
This tells the development team that your pull request is a "work-in-progress", and that you plan to continue working on it.

Review and discussion on new code can begin well before the work is complete, and the more discussion the better!
The development team may prefer a different path than you've outlined, so it's better to discuss it and get approval at the early stage of your work.

Once your PR is ready, a member of the development team will review your changes to confirm that they can be merged into the main codebase.

## Notes for New Code

#### Testing
Testing is a crucial step of code development, remember:
- new code should be tested
- bug fixes should include an example that exposes the issue
- any new features should have tests that show at least a minimal example.

If you're not sure what this means for your code, please ask in your pull request,
we will help you with writing the tests.


[link_hipporeport]: https://github.com/Australian-Epilepsy-Project/protocol_assurance
[link_signupinstructions]: https://help.github.com/articles/signing-up-for-a-new-github-account
[link_new_issues]: https://github.com/Australian-Epilepsy-Project/protocol_assurance/issues/new/choose
[link_doc_issues]: https://github.com/Australian-Epilepsy-Project/protocol_assurance/issues/new?assignees=&labels=documentation&template=documentation.md&title=

[link_pullrequest]: https://help.github.com/articles/creating-a-pull-request-from-a-fork/
[link_branch]: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-and-deleting-branches-within-your-repository
[link_clone]: https://help.github.com/articles/cloning-a-repository/
[link_updateupstreamwiki]: https://help.github.com/articles/syncing-a-fork/
[link_push]: https://help.github.com/en/github/using-git/pushing-commits-to-a-remote-repository
[link_commit]: https://git-scm.com/docs/git-commit
