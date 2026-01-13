#!/usr/bin/env bash

# --------------------------
# Сообщение коммита
# --------------------------
if [ -z "$1" ]; then
  commit_message="Update ($(LANG=en_EN date +'%a, %b %d, %Y %r'))"
else
  commit_message="$1 ($(LANG=en_EN date +'%a, %b %d, %Y %r'))"
fi

echo "Сообщение коммита: $commit_message"


# --------------------------
# Git workflow
# --------------------------
git add .

git commit -m "$commit_message"

current_branch=$(git branch --show-current)
if [ -z "$current_branch" ]; then
  current_branch="main"
  git branch -M main
fi

git push -u origin $current_branch

echo "Коммит и пуш выполнены!"