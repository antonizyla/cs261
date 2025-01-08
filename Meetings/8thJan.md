- Antoni
- Krister
- Thomas
- Eshan
- Josh

Everyone has used Java, Python and has basic web dev experience. 

Design a solution based on creating arbitrary traffic juntions to minimise following
1. Average wait time in each direction.
2. Maximum wait time in each direction.
3. Maximum queue length in each direction.

## Key Functionality
1. All input and output paramaters taken into account
2. Backend in Java - Junit unit testing
    - do simulation and calculations entirely on backend
    - add 2 endpoints - one for returning report on a set of params and one for verifiying that a set of params is valid (keep one source of truth)
3. Simple Rest Api for stats based on parameters
4. Frontend web based in nextjs + tailwind
    - Input the parameters
    - Visual representation of what the junction looks like based on parameters
    - Generate pdf report of performance - fetch from backend
5. Generate PDF based summary of how good a set of parameters perform - do on backend or maybe just display in markdown on frontend?
6. Allow for comparison of performance between different sets of parameters
7. Configurable params
    - Number of Lanes
    - Left Turn Lane
    - need to see if we need to implement all or just some of these
8. Consider packaging into a docker container for portability.