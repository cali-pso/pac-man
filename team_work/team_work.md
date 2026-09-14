# Pac-Man Project: Team Work Recap

### Timeline & Delivery
We initially gave ourselves a comfy one-month buffer to get everything done. But we really pushed through and actually managed to finish the whole thing in about two weeks! 

### Development Workflow
We took a pretty logical, step-by-step approach to building this. We started off by setting up the menu, then built the parser, and got the maze rendering on screen. Once we could see the maze, we focused on the core playability. After the base game felt right, we threw in the sprites and music, built out the different game modes, and wrapped up with all the miscellaneous polish.

### Scope Adjustments
We definitely had to dial back our initial expectations to keep things realistic and ship on time. We completely dropped the idea of a 3D mode. For the Roguelite mode, we skipped the persistent in-maze bonuses and the unlockable extra modifiers. We also scrapped the 'smoker mode' idea and decided not to stress over recreating the *exact* ghost algorithms from the original arcade game.

### Team Organization
We didn't have a rigid master plan—we just organized things on the fly. We divided up the tasks based on whatever the project needed most at that exact moment. Even with this spontaneous style, we kept things clean by using separate Git branches so we weren't constantly stepping on each other's code.

### Pending Tasks
The main thing left on our to-do list is Beta Testing. We just need to get some runs in and make sure everything is completely solid.

### Technical Challenges
We hit some pretty frustrating roadblocks getting the animations and character movement to feel right. We ended up working through it with some help from AI, and the magic fix was implementing a fixed framerate. That really smoothed everything out.

### Design & Technical Decisions
We had to make a big call regarding the Shadow mode. We ultimately decided *not* to display the walls in the shadows. It came down to a performance and design trade-off: drawing only the visible parts of the maze every single frame versus rendering the whole maze once at load time and masking it.

