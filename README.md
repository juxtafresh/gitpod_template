**Shorts Automation**

## System Design

```mermaid
graph TD;
    id1(Hypothesis Gen Module) --> id2(Execution module);
    id2(Execution module) --> id3(Harvest Module);
    id3(Harvest Module) --> id4[Data Module];
    id4[Data Module] --> id5(Anaysis Module);
    id5(Anaysis Module) --> id4[Data Module];
    id5(Anaysis Module) --> id1(Hypothesis Gen Module);
```

### Inspirations:
 > https://github.com/anna-geller/dataflow-ops
 > https://medium.com/the-prefect-blog/declarative-dataflow-deployments-with-prefect-make-ci-cd-a-breeze-fe77bdbb58d4


### Should add better memaid:
https://mermaid.js.org/syntax/classDiagram.html

### Open Questions
Can I just do a local polling agent with prefect for the time being?
    No should figure out how to host via pulumi and have some version of anna's ci cd automation via gitlab
