# Contributing

The only rule is document and test as much as possible.

This project tries to have as less dependencies as possible to avoid problems
with deploying.

Code does not necessarily need to be document, it should be rather self
explanatory.

## Commit + Pull Request workflow

1. Fork the repository and clone it into your local development machine

2. [HACK](HACKING.md)

3. Create commits for logical changes - it is better to create more commits
   than less

4. Use the short commit message to provide an apt description of the change.
   Write the short message in the imperative, present tense.

5. Use the commit message body to explain your motivation and document your
   thinking process (to put it simple - care to explain "why"). Everybody can
   see the changes made, so do not try to summarize them unless you changed
   dozens of files. In the case you change visible output, it is a good idea to
   provide current version and the new one.

6. Open a pull request - if you see Merge commits in your PR, you did something
   wrong, so please try to get rid of them

7. Check GitHub Actions builder

8. In case of build failures, please, **amend your commits** - IOW try to avoid adding
   new commits fixing your commits to your pull request

9. If a reviewer request changes, try to amend existing commits

10. When you amend a commit, please add a new line with '--- vX' where X is the
   number of version of the commit and describe the changes to the commit below
   that line

11. To keep history linear and easy to understand, your pull request commits
   will be either Squashed or more likely your PR branch will be merged with
   Rebase

12. When your PR is merged, you need to do **Rebase** too to synchronize your local
    master branch - `git pull -r` or `git fetch upstream && git rebase upstream/master`
