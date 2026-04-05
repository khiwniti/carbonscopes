# TREES NC 1.1 RDF Schema Documentation

## Overview

This documentation covers the TREES (Thai Rating of Energy and Environmental Sustainability) NC 1.1 RDF ontology for green building certification in Thailand.

**Schema Files:**
- **Ontology**: `/backend/knowledge_graph/schemas/trees-nc-1.1.ttl`
- **Example Data**: `/backend/knowledge_graph/schemas/trees-nc-1.1-example.ttl`
- **Documentation**: This file

**Namespace**: `http://tgbi.or.th/trees/ontology#`
**Prefix**: `trees`
**Version**: 1.1
**GraphDB Repository**: `carbonbim-thailand`

---

## TREES NC 1.1 Certification System

### Certification Levels

| Level | Points Required | Description |
|-------|----------------|-------------|
| **Certified** | 50-59 points | Entry-level green building certification |
| **Gold** | 60-79 points | Strong environmental performance |
| **Platinum** | 80-100 points | Exceptional sustainability leadership |

### Rating Categories

| Category | Code | Max Points | Focus Area |
|----------|------|------------|------------|
| Site & Landscape | SL | 9 | Site planning, landscape, heat island |
| Water Efficiency | WE | 12 | Water conservation, fixtures, reuse |
| Energy & Atmosphere | EA | 32 | Energy efficiency, renewables, emissions |
| **Materials & Resources** | **MR** | **15** | **Sustainable materials, green labels, reuse** |
| Indoor Environmental Quality | IEQ | 16 | Air quality, comfort, lighting |
| Environmental Management | EM | 10 | Management systems, innovation |
| Green Innovation | GI | 6 | Innovation, exceptional performance |
| **Total** | | **100** | |

---

## Materials & Resources (MR) Criteria

This ontology focuses on two key MR criteria:

### MR1: Green/Carbon Labeled Materials

**Requirement**: Minimum 30% of total material cost must have recognized environmental certification labels.

**Recognized Labels:**
- TGO Carbon Label (ฉลากคาร์บอนฟุตพริ้นท์ของผลิตภัณฑ์)
- Thai Green Label (ฉลากเขียว)
- FSC (Forest Stewardship Council)
- Cradle to Cradle Certified
- ISO Type I Environmental Labels
- EPD (Environmental Product Declaration)
- Other TGBI-approved labels

**Points**: 10 points maximum (all-or-nothing: 30% = 10 points, <30% = 0 points)

**Calculation**:
```
Green Material Percentage = (Green Material Cost / Total Material Cost) × 100
If >= 30%: Award 10 points
If < 30%: Award 0 points
```

### MR3: Reused Materials

**Requirement**: Use salvaged, reclaimed, or refurbished materials and components.

**Qualifying Materials:**
- Salvaged materials from demolition sites
- Reclaimed timber, bricks, steel
- Refurbished doors, windows, fixtures
- Architectural elements from historic buildings
- Factory seconds or surplus materials

**Points**: 5 points maximum (scaled)

**Calculation**:
```
Reused Material Percentage = (Reused Material Cost / Total Material Cost) × 100
If >= 10%: Award 5 points (maximum)
If >= 5% and < 10%: Award 3 points
If < 5%: Award 0 points
```

### Cost Basis Rules

- Based on actual material purchase price (excluding labor)
- Material cost excludes:
  - MEP (Mechanical, Electrical, Plumbing) equipment
  - Furniture and movable items
  - Finishes in some cases (refer to TREES guidelines)
- Must be documented with invoices and certificates
- For reused materials: use current replacement value

---

## OWL Schema Design

### Key Classes

```turtle
# Certification Levels
trees:Certification (base class)
  ├── trees:Certified (50-59 points)
  ├── trees:Gold (60-79 points)
  └── trees:Platinum (80-100 points)

# Material Resource Criteria
trees:MaterialsCriterion (base class)
  ├── trees:GreenLabeledMaterialsCriterion (MR1)
  └── trees:ReusedMaterialsCriterion (MR3)

# Material Usage
trees:MaterialUsage (base class)
  ├── trees:GreenLabeledMaterial (for MR1)
  └── trees:ReusedMaterial (for MR3)

# Assessment
trees:MaterialsAssessment
trees:Project
trees:BuildingType
```

### OWL Best Practices Applied

Following EDGE V3 schema patterns:

1. **Property Types**:
   - `owl:ObjectProperty` for object references (e.g., `trees:usesConstructionMaterial`)
   - `owl:DatatypeProperty` for literal values (e.g., `trees:materialCost`)
   - `owl:FunctionalProperty` for properties with max cardinality 1

2. **Cardinality Constraints**:
   ```turtle
   trees:MaterialUsage
       rdfs:subClassOf [
           rdf:type owl:Restriction ;
           owl:onProperty trees:materialQuantity ;
           owl:minCardinality "1"^^xsd:nonNegativeInteger
       ] .
   ```

3. **Specific XSD Datatypes**:
   - `xsd:decimal` for costs and percentages
   - `xsd:integer` for points
   - `xsd:date` for dates
   - `xsd:string` for text
   - `xsd:boolean` for flags

4. **Inverse Properties**:
   ```turtle
   trees:hasMaterialsAssessment owl:inverseOf trees:isAssessmentOf
   ```

5. **Bilingual Labels**:
   ```turtle
   trees:Gold
       rdfs:label "TREES Gold"@en ;
       rdfs:label "TREES ระดับทอง"@th .
   ```

---

## Integration with TGO

The TREES ontology integrates with the TGO (Thailand Greenhouse Gas Management Organization) ontology:

```turtle
# Link material usage to TGO materials
ex:ConcreteUsage
    trees:usesConstructionMaterial tgo:ReadyMixConcrete_30MPa ;
    trees:materialQuantity "2500.0"^^xsd:decimal ;
    trees:materialCost "3750000.0"^^xsd:decimal .

# TGO provides emission factors
tgo:ReadyMixConcrete_30MPa
    tgo:hasEmissionFactor "450.0"^^xsd:decimal ;
    tgo:hasUnit "kgCO2e/m3" .
```

**Benefits**:
- Centralized material database
- Consistent emission factors
- Green label verification
- Material property inheritance

---

## SPARQL Query Examples

### 1. Check MR1 Compliance

```sparql
PREFIX trees: <http://tgbi.or.th/trees/ontology#>

SELECT ?project ?greenPercentage ?mr1Points ?status
WHERE {
  ?project trees:hasMaterialsAssessment ?assessment .
  ?assessment trees:greenLabeledPercentage ?greenPercentage ;
              trees:mr1Points ?mr1Points ;
              trees:complianceStatus ?status .
  FILTER (?greenPercentage >= 30.0)
}
```

**Use Case**: Verify which projects meet the 30% green-labeled material requirement.

---

### 2. Calculate MR3 Points Based on Reused Percentage

```sparql
PREFIX trees: <http://tgbi.or.th/trees/ontology#>

SELECT ?project ?reusedPercentage
       (IF(?reusedPercentage >= 10.0, 5,
           IF(?reusedPercentage >= 5.0, 3, 0)) AS ?mr3Points)
WHERE {
  ?project trees:hasMaterialsAssessment ?assessment .
  ?assessment trees:reusedPercentage ?reusedPercentage .
}
```

**Use Case**: Calculate MR3 points for all projects based on reused material percentage.

---

### 3. List All Green-Labeled Materials in Project

```sparql
PREFIX trees: <http://tgbi.or.th/trees/ontology#>
PREFIX tgo: <http://tgo.or.th/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?material ?label ?labelType ?cost ?certNumber
WHERE {
  ?usage rdf:type trees:GreenLabeledMaterial ;
         trees:usesConstructionMaterial ?tgoMaterial ;
         trees:greenLabelType ?labelType ;
         trees:materialCost ?cost ;
         trees:greenLabelCertificateNumber ?certNumber .
  ?tgoMaterial rdfs:label ?label .
  FILTER (lang(?label) = "en")
}
ORDER BY DESC(?cost)
```

**Use Case**: Generate a report of all green-labeled materials with costs and certificates.

---

### 4. Calculate Total MR Category Points

```sparql
PREFIX trees: <http://tgbi.or.th/trees/ontology#>

SELECT ?project ?projectName ?mr1Points ?mr3Points
       (?mr1Points + ?mr3Points AS ?totalMRPoints)
WHERE {
  ?project trees:projectName ?projectName ;
           trees:hasMaterialsAssessment ?assessment .
  ?assessment trees:mr1Points ?mr1Points ;
              trees:mr3Points ?mr3Points .
}
ORDER BY DESC(?totalMRPoints)
```

**Use Case**: Rank projects by total Materials & Resources category performance.

---

### 5. Verify Certification Level Eligibility

```sparql
PREFIX trees: <http://tgbi.or.th/trees/ontology#>

SELECT ?project ?projectName ?totalPoints
       (IF(?totalPoints >= 80, "Platinum",
           IF(?totalPoints >= 60, "Gold",
              IF(?totalPoints >= 50, "Certified", "Not Certified"))) AS ?eligibleLevel)
WHERE {
  ?project trees:projectName ?projectName ;
           trees:hasMaterialsAssessment ?assessment .
  ?assessment trees:totalPoints ?totalPoints .
}
ORDER BY DESC(?totalPoints)
```

**Use Case**: Determine certification level eligibility for all projects.

---

### 6. Find Materials with Both Green Labels AND Reuse

```sparql
PREFIX trees: <http://tgbi.or.th/trees/ontology#>
PREFIX tgo: <http://tgo.or.th/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?material ?label ?greenLabelType ?reuseCategory ?cost
WHERE {
  ?usage trees:usesConstructionMaterial ?tgoMaterial ;
         trees:hasGreenLabel ?hasLabel ;
         trees:greenLabelType ?greenLabelType ;
         trees:isReused ?isReused ;
         trees:reuseCategory ?reuseCategory ;
         trees:materialCost ?cost .
  ?tgoMaterial rdfs:label ?label .
  FILTER (?hasLabel = true && ?isReused = true)
  FILTER (lang(?label) = "en")
}
```

**Use Case**: Identify materials that contribute to both MR1 and MR3 (double benefit).

---

### 7. Calculate Cost Breakdown for MR Criteria

```sparql
PREFIX trees: <http://tgbi.or.th/trees/ontology#>

SELECT ?project ?projectName ?totalCost ?greenCost ?reusedCost
       (?greenCost * 100.0 / ?totalCost AS ?greenPct)
       (?reusedCost * 100.0 / ?totalCost AS ?reusedPct)
WHERE {
  ?project trees:projectName ?projectName ;
           trees:hasMaterialsAssessment ?assessment .
  ?assessment trees:totalMaterialCost ?totalCost ;
              trees:greenLabeledMaterialCost ?greenCost ;
              trees:reusedMaterialCost ?reusedCost .
}
```

**Use Case**: Generate financial summary showing investment in green and reused materials.

---

### 8. Identify Top Cost Contributors (Pareto Analysis)

```sparql
PREFIX trees: <http://tgbi.or.th/trees/ontology#>
PREFIX tgo: <http://tgo.or.th/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?material ?label ?cost
       (?cost * 100.0 / ?totalCost AS ?costPercentage)
WHERE {
  ?project trees:hasMaterialsAssessment ?assessment .
  ?assessment trees:totalMaterialCost ?totalCost .

  ?usage trees:usesConstructionMaterial ?tgoMaterial ;
         trees:materialCost ?cost .
  ?tgoMaterial rdfs:label ?label .
  FILTER (lang(?label) = "en")
}
ORDER BY DESC(?cost)
LIMIT 10
```

**Use Case**: Focus optimization efforts on highest-cost materials (80/20 rule).

---

### 9. Track Reused Material Sources

```sparql
PREFIX trees: <http://tgbi.or.th/trees/ontology#>
PREFIX tgo: <http://tgo.or.th/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?material ?label ?reuseCategory ?source ?cost
WHERE {
  ?usage rdf:type trees:ReusedMaterial ;
         trees:usesConstructionMaterial ?tgoMaterial ;
         trees:reuseCategory ?reuseCategory ;
         trees:materialSource ?source ;
         trees:materialCost ?cost .
  ?tgoMaterial rdfs:label ?label .
  FILTER (lang(?label) = "en")
}
ORDER BY DESC(?cost)
```

**Use Case**: Document circular economy practices and material provenance.

---

### 10. Find Projects Near Certification Threshold

```sparql
PREFIX trees: <http://tgbi.or.th/trees/ontology#>

SELECT ?project ?projectName ?totalPoints
       (60 - ?totalPoints AS ?pointsNeededForGold)
WHERE {
  ?project trees:projectName ?projectName ;
           trees:hasMaterialsAssessment ?assessment .
  ?assessment trees:totalPoints ?totalPoints .
  FILTER (?totalPoints >= 50 && ?totalPoints < 60)
}
ORDER BY DESC(?totalPoints)
```

**Use Case**: Identify projects that need small improvements to reach Gold certification.

---

### 11. Compare Green Label Types Distribution

```sparql
PREFIX trees: <http://tgbi.or.th/trees/ontology#>

SELECT ?labelType
       (COUNT(?usage) AS ?materialCount)
       (SUM(?cost) AS ?totalCost)
WHERE {
  ?usage rdf:type trees:GreenLabeledMaterial ;
         trees:greenLabelType ?labelType ;
         trees:materialCost ?cost .
}
GROUP BY ?labelType
ORDER BY DESC(?totalCost)
```

**Use Case**: Analyze which green labels are most commonly used and valuable.

---

### 12. Audit Trail Query

```sparql
PREFIX trees: <http://tgbi.or.th/trees/ontology#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?project ?projectName ?assessmentDate ?assessorName
       ?verificationDate ?verifierName
WHERE {
  ?project trees:projectName ?projectName ;
           trees:hasMaterialsAssessment ?assessment .
  ?assessment trees:assessmentDate ?assessmentDate ;
              trees:assessedBy ?assessor ;
              trees:verificationDate ?verificationDate ;
              trees:verifiedBy ?verifier .
  ?assessor foaf:name ?assessorName .
  ?verifier foaf:name ?verifierName .
}
ORDER BY DESC(?verificationDate)
```

**Use Case**: Track certification timeline and responsible parties for audit purposes.

---

## Example Instance

See `trees-nc-1.1-example.ttl` for a complete example of:
- **Project**: Sustainable Tower Bangkok (15,000 m² office building)
- **Certification**: TREES Gold target
- **Green-Labeled Materials**: 38% of cost (10 points for MR1)
  - TGO Carbon Label concrete
  - Thai Green Label steel and tiles
  - FSC certified timber
  - Cradle to Cradle glass
  - ISO Type I aluminum panels
  - EPD insulation
- **Reused Materials**: 6% of cost (3 points for MR3)
  - Salvaged timber from warehouse
  - Reclaimed bricks from historic building
  - Refurbished fire-rated doors
- **Total MR Points**: 13/15

---

## Validation Rules

### Data Quality Checks

1. **Percentage Consistency**:
   ```sparql
   # Verify percentages match cost calculations
   SELECT ?project
   WHERE {
     ?project trees:hasMaterialsAssessment ?assessment .
     ?assessment trees:greenLabeledMaterialCost ?greenCost ;
                 trees:totalMaterialCost ?totalCost ;
                 trees:greenLabeledPercentage ?greenPct .
     BIND((?greenCost * 100.0 / ?totalCost) AS ?calculatedPct)
     FILTER (ABS(?greenPct - ?calculatedPct) > 0.1)
   }
   ```

2. **Points Consistency**:
   ```sparql
   # Verify MR1 points match percentage threshold
   SELECT ?project
   WHERE {
     ?project trees:hasMaterialsAssessment ?assessment .
     ?assessment trees:greenLabeledPercentage ?pct ;
                 trees:mr1Points ?points .
     FILTER ((?pct >= 30 && ?points != 10) || (?pct < 30 && ?points != 0))
   }
   ```

3. **Cost Sum Validation**:
   ```sparql
   # Check if individual material costs sum to total
   SELECT ?project ?declaredTotal ?calculatedTotal
   WHERE {
     ?project trees:hasMaterialsAssessment ?assessment .
     ?assessment trees:totalMaterialCost ?declaredTotal .

     {
       SELECT ?project (SUM(?cost) AS ?calculatedTotal)
       WHERE {
         ?project trees:hasMaterialUsage ?usage .
         ?usage trees:materialCost ?cost .
       }
       GROUP BY ?project
     }
     FILTER (ABS(?declaredTotal - ?calculatedTotal) > 1.0)
   }
   ```

---

## Best Practices

### Material Documentation

1. **Green Labels**: Always include certificate numbers
2. **Reused Materials**: Document source and date of salvage/reclamation
3. **Costs**: Use actual invoiced amounts, exclude labor
4. **Quantities**: Match TGO functional units (kg, m³, m², pieces)

### Assessment Workflow

1. **Data Collection**: Gather BOQ (Bill of Quantities) and material invoices
2. **TGO Mapping**: Link materials to TGO ontology entries
3. **Label Verification**: Confirm green label certificates with suppliers
4. **Cost Calculation**: Sum costs by category (green, reused, standard)
5. **Percentage Calculation**: Compute green and reused percentages
6. **Point Allocation**: Apply TREES NC 1.1 rules
7. **Audit Trail**: Document assessor and verifier

### Common Pitfalls

❌ **Don't**:
- Include MEP equipment in material cost
- Count furniture or movable fixtures
- Use estimated costs (must be actual invoices)
- Include labor/installation costs
- Double-count materials in both MR1 and MR3 costs

✅ **Do**:
- Verify green label certificates are current
- Document reused material sources
- Use replacement value for reused materials
- Keep detailed cost breakdowns
- Maintain audit trail

---

## Repository Configuration

### GraphDB Setup

```turtle
# Repository: carbonbim-thailand
# Ruleset: OWL-RL (Optimized)
# Inference: Enabled

# Import sequence:
1. tgo_ontology.ttl          # TGO base ontology
2. trees-nc-1.1.ttl          # TREES ontology (imports TGO)
3. trees-nc-1.1-example.ttl  # Example instance data
```

### Named Graphs (Optional)

```sparql
# Load into named graphs for versioning
LOAD <file:///trees-nc-1.1.ttl> INTO GRAPH <http://tgbi.or.th/trees/schema/v1.1>
LOAD <file:///trees-nc-1.1-example.ttl> INTO GRAPH <http://example.org/projects/2026>
```

---

## Performance Considerations

### Indexing

Key properties for indexing:
- `trees:projectID`
- `trees:greenLabeledPercentage`
- `trees:reusedPercentage`
- `trees:totalPoints`
- `trees:assessmentDate`

### Query Optimization

1. **Use FILTER early**: Reduce result set size
2. **Limit language tags**: `FILTER (lang(?label) = "en")`
3. **Aggregate efficiently**: Use `GROUP BY` with caution
4. **Cache common queries**: Store results of certification level checks

---

## References

- **TGBI Official**: https://tgbi.or.th
- **TREES NC 1.1 Manual**: (Contact TGBI for official documentation)
- **TGO Website**: https://tgo.or.th
- **EDGE V3 Schema**: See `edge-v3.ttl` for similar OWL patterns
- **RDF/OWL Best Practices**: https://www.w3.org/TR/owl2-primer/

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.1 | 2026-03-23 | Initial release with MR1 and MR3 criteria |

---

## License

Open for TREES certified projects. Contact TGBI for commercial use.

---

## Contact

For questions or contributions:
- **Schema Issues**: BKS cBIM AI Platform team
- **TREES Certification**: TGBI (Thai Green Building Institute)
- **TGO Integration**: TGO (Thailand Greenhouse Gas Management Organization)
