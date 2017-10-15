
# Features de base de git 


## Gestion des branches 

Vous pouvez voir en bas à droite écrit 0.basic_git, qui est le nom de la branche. 
Dans le cas contraire, vérifiez que vous avez bien le plugin git de pycharm

### changement de branche

En cliquant dessus vous devez voir appraître un menu, qui se décompose en 3 parties :

- création d'une nouvelle branche 
- branches locales
- branches distantes

Maintenant cliquez dans les branches distantes sur la branche 0.basic_git, 
puis séléctioner "checkout as new local branch" (premier choix).

Vous savez maintenant changer de branche ! 
On utilisera par la suite cette méthode pour avancer dans le TP

### création de branche 

Vous pouvez maintenant créer votre propre branche. Essayer de créer la branche 0.2.my_first_commit.


### commit 

Pour prendre en compte des modifications, vous devez commit. 
Allez dans le fichier file_to_change.txt et faites le changement suggéré.
Sur le menu de projet (à gauche), faites un click droit sur le fichier que vous venez de modifier puis selectionez 
git > commit file.
Cela va vous ouvrir un menu pour commit. Mettez le commit message de votre choix (par exemple 
"ceci est un message de commit qui ne m'aide pas du tout à savoir quelles modifications ont été excecutées, donc il est déconseillé"), 
puis clicker sur commit.


### Comparez deux branches

Vous pouvez comparez votre branche crée avec celle de base en faisant 0.basic_git > comparer.
Votre branche en cours est censée avoir un commit de plus que la branche 0.basic_git


### merge

Faites un checkout sur la branche 0.basic_git, et commitez un fichier vide.
Retournez sur la branche 0.1, puis faires 0.basic_git > merge.
Le fichier vide devrait être rajouté sur votre branche 0.1.


### merge conflict

Faites un checkout sur la branche 0.basic_git, et commitez changement sur file_to_change.txt (par exemple ajouter "a" à la fin du fichier).
Retournez sur la branche 0.1, puis commitez un autre changement sur file_to_change.txt (par exemple ajouter "b" à la fin du fichier)

faires 0.basic_git > merge.
Le merge comporte ici un conflit, ce qui devrait vous ouvrir une interface graphique pour les résoudre.


## Pour ceux qui ont fini


### logs 

Vous pouvez regarder l'historique des commits en allant sur l'onglet 9: version control en bas à gauche.

### rebase

Faites l'exercice du merge, mais maintenant en faisant la commande rebase.
Vous devriez pouvoir voir une différence dans l'ordonnancement des commits provenant de la branche principale.



