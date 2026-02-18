# monkey testing

- when there is missing scores, a message shows when trying to compute saying it is missing scores. This is fine, but it refers to their UUID instead of their name, that is not useful
- Enter still does not work to "enter a competition screen"
- provide a way to delete a competition on the home screen
- the transcript panel should be hidden by default
- The transcript and thus the score algorithm works fine. The dead cells display state a little less some of the cells should be inactive like in example of rule 6 and 7 some ranks are defined at the same time in the same column (happens when tie break tipically). In other words the matrix does not illustrate well the transcript in tie breaks by often not deactivating a column early enough.
- When exiting the competion editing screen (back to home) the home table should be updated (names changes but are not refreshed right now)
- control c is not working for copy. I think it is because it is supposed to be for quitting.
