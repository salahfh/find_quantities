## Issues:
* If a product quantity is negative (return) but there is no postive product to match it with
   the inventory should hand them correctly. (Possible solution: Recode them as positive stock and negative price)
* Add support different levels of R reminder to allow the solve to find an optimal solution
* Add output message/status to the commands
* Add column selection configs
* Extract solver configs
* Do I need to change the assignment percentages?

* Iteration of improvements:
   1. No tolerance interval
   2. Interval tolerance
   3. Interval tolerence with variable product percetage
   4. Previous one plus taking negative stock into consideration - bug in inventory function
   5. Better results


CLV-LUX16X - Month 4 - returned product getting doubled? 