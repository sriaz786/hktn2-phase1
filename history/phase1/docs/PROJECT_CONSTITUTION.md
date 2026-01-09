# Evolution of Todo Project Constitution

**Version:** 1.0
**Scope:** Global - Applies to all phases (1-5)
**Authority:** This constitution supersedes all ad-hoc decisions. No agent or human may violate its terms.

---

## 1. Spec-Driven Development (MANDATORY)

### 1.1 Development Workflow
All development MUST follow this exact sequence:

```
Constitution → Specification → Plan → Tasks → Implementation
```

**Breaking any link in this chain is a violation.**

### 1.2 Code Production Rules
- **No agent may write production code without an approved specification**
- **No agent may write production code without an approved task list derived from an approved plan**
- Every code change must trace back to:
  1. A specific requirement in an approved Specification
  2. A specific step in an approved Plan
  3. A specific task in an approved Task List

### 1.3 Enforcement
- Before any implementation: Verify specification exists and is approved
- Before any implementation: Verify plan exists and is approved
- Before any implementation: Verify tasks exist and are approved
- Any violation requires immediate rollback and proper workflow completion

---

## 2. Agent Behavior Rules

### 2.1 No Manual Human Coding
- **Humans may NOT write production code**
- Humans may only:
  - Write/update specifications
  - Approve specifications, plans, and tasks
  - Provide feedback and direction
  - Review and approve code
- All code writing is performed exclusively by agents

### 2.2 No Feature Invention
- Agents may NOT add features not specified in approved specifications
- Agents may NOT add "nice-to-have" enhancements without specification
- Agents may NOT solve problems beyond the defined scope
- If a gap or missing requirement is discovered:
  - STOP implementation
  - Report the gap to specification phase
  - Do NOT proceed until specification is updated and approved

### 2.3 No Deviation from Specifications
- Code must EXACTLY implement approved specifications
- "Creative improvements" are violations unless specified
- Architecture decisions must match specifications exactly
- Technology choices must match technology constraints exactly

### 2.4 Refinement Location
- **Refinement occurs at SPECIFICATION level, NOT code level**
- If code needs to change due to new understanding:
  1. Stop coding
  2. Update the specification
  3. Get specification approved
  4. Update the plan
  5. Get plan approved
  6. Update tasks
  7. Get tasks approved
  8. Only then resume coding
- Code-level patches to address spec-level issues are violations

---

## 3. Phase Governance

### 3.1 Phase Boundaries
Each phase is **strictly scoped** by its specification:
- Phase 1: Initial scope as defined in Phase 1 Spec
- Phase 2: Initial scope as defined in Phase 2 Spec
- Phase 3: Initial scope as defined in Phase 3 Spec
- Phase 4: Initial scope as defined in Phase 4 Spec
- Phase 5: Initial scope as defined in Phase 5 Spec

### 3.2 Future-Phase Containment
- **Future-phase features must NEVER leak into earlier phases**
- Phase 1 must NOT contain Phase 2+ features
- Phase 2 must NOT contain Phase 3+ features
- Phase 3 must NOT contain Phase 4+ features
- Phase 4 must NOT contain Phase 5 features
- Violation example: Adding websockets in Phase 1 when scheduled for Phase 3

### 3.3 Architecture Evolution
- Architecture may ONLY evolve through:
  1. Updated specifications
  2. Approved plans
  3. Executed tasks
- Spontaneous architectural changes are violations
- "Preparation for future phases" without specification is a violation
- If architecture needs to change:
  - Create/update specification for the change
  - Get specification approved
  - Create/update plan
  - Get plan approved
  - Execute tasks

---

## 4. Technology Constraints

### 4.1 Mandatory Technology Stack

#### Backend (All Phases)
- **Language:** Python
- **Framework:** FastAPI
- **Database ORM:** SQLModel
- **Database:** Neon DB (PostgreSQL)
- **AI Integration:** OpenAI Agents SDK
- **Protocol:** MCP (Model Context Protocol)

#### Frontend (Phase 3+)
- **Framework:** Next.js
- **Additional:** React (as part of Next.js stack)
- **Note:** No frontend before Phase 3

#### Infrastructure (Phase 4+)
- **Containerization:** Docker
- **Orchestration:** Kubernetes
- **Message Broker:** Kafka
- **Resilience:** DRP (Disaster Recovery Plan)

### 4.2 Technology Usage Rules
- **Use ONLY technologies listed above**
- No additional dependencies without specification
- No alternative implementations without specification
- No technology upgrades without specification
- Example: Don't swap SQLModel for SQLAlchemy without spec approval

### 4.3 Phase-Specific Availability
- **Phase 1:** Python, FastAPI, SQLModel, Neon DB, OpenAI Agents SDK, MCP
- **Phase 2:** Same as Phase 1 (backend-focused)
- **Phase 3:** Add Next.js for frontend
- **Phase 4:** Add Docker, Kubernetes
- **Phase 5:** Add Kafka, DRP

---

## 5. Quality Principles

### 5.1 Clean Architecture
- Use dependency inversion where appropriate
- Boundaries between layers must be explicit
- Business logic independent of frameworks
- Database as implementation detail, not architecture driver
- Testable design

### 5.2 Stateless Services
- Services should be stateless where possible
- State should live in the database or cache
- Avoid in-memory state in long-running services
- Enables horizontal scaling

### 5.3 Separation of Concerns
- Clear boundaries between:
  - Domain logic
  - Application logic
  - Infrastructure logic
  - Presentation logic (Phase 3+)
- Each module/component has a single responsibility
- Avoid god classes and god services

### 5.4 Code Quality Standards
- Type hints required for all Python code
- Docstrings for public APIs
- Meaningful variable and function names
- Small, focused functions
- DRY principle (Don't Repeat Yourself)
- No commented-out code in production

### 5.5 Testing
- Unit tests for business logic
- Integration tests for critical paths
- No testing in production
- Tests must pass before merging

---

## 6. Process Enforcement

### 6.1 Pre-Implementation Checklist
Before writing ANY production code:

- [ ] Specification exists and is approved
- [ ] Plan exists and is approved
- [ ] Tasks exist and are approved
- [ ] Task is currently in "in_progress" state
- [ ] Technology choices match this constitution
- [ ] No violation of phase boundaries
- [ ] All dependencies are specified

### 6.2 Violation Handling
Any constitution violation must:
1. Be identified and reported immediately
2. Trigger rollback of violating changes
3. Initiate process correction through proper workflow
4. Be documented in project history

### 6.3 Continuous Compliance
- Regular reviews of codebase against constitution
- Constitution may be updated only through:
  - Specification change
  - Plan approval
  - Documented amendment process

---

## 7. Project Philosophy

### 7.1 Purpose
This constitution exists to ensure:
- Predictable, traceable development
- Controlled scope and evolution
- High-quality, maintainable code
- Clear boundaries between phases
- No scope creep or feature bloat

### 7.2 Success Metrics
- All code traceable to specifications
- Zero violations of phase boundaries
- Zero unauthorized technology additions
- Zero manual code commits by humans
- All changes follow Constitution → Spec → Plan → Tasks → Implement workflow

---

## 8. Emergency Protocol

If this constitution seems to block critical progress:
1. Do NOT violate the constitution
2. Identify the blocking issue
3. Create specification amendment
4. Get amendment approved
5. Proceed through proper workflow
6. Constitution violations are NEVER acceptable shortcuts

---

## 9. Ratification

**This constitution is effective immediately upon creation.**
**All agents and humans must abide by its terms.**
**No exceptions.**

---

*Constitution created for Evolution of Todo project*
*Version 1.0*
*Date: 2025-01-06*
