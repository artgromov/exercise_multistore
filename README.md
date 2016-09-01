# MultiStore class to manage state dependencies
This is my proof of concept class that can automatically recalc dependent attributes.

# Roadmap
* [x] Write MultiStore class that maintain attribute dependencies
* [x] Class methods should recalculate attributes with respect to their dependencies
* [x] Custom logic and validators should be possible to add in any order
* [ ] Optimize loop search algorithm by rewrite get_recalc_order as generator function
