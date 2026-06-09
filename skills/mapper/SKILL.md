---
name: mapper
description: Generate a Java mapper/translator method that maps fields from a source model to a target model
user_invocable: true
arguments:
  - name: source-class
    description: Path to the class where the mapping functions should be created.
    required: true
  - name: source-model
    description: Path to the source model class (input parameter of the mapper)
    required: true
  - name: target-model
    description: Path to the target model class (return type of the mapper)
    required: true
  - name: paper-mapping
    description: Path to a paper mapping (field mapping documentation)
    required: false
---

# Mapper Generator Skill

You are generating a Java mapper method inside of the **source class** that translates a **source model** into a **target model**. If a **paper-mapping** argument is provided you will do the field mapping based on paper mapping.

## Instructions

1. **Read both model files** provided as arguments. The first argument is the source model (input), the second is the target model (output/return type).

2. **Analyze both models**: Extract all fields, their types, getter/setter methods, and any annotations (`@XmlElement`, `@JsonProperty`, JFESA annotations, etc.) to understand the field names and types.

3. **Analyse paper-mapping** If the **paper-mapping** argument is provided you will also read and analyse this document. Paper mappings are not always structured the same way, but will always contain intructions on how fields should be mapped. Try to detect how to **source-model** must be against the **target-model**

4. **Generate a mapper method** following this pattern from the codebase:

```java
private TargetModel createTargetModel(SourceModel sourceModel) {
    final TargetModel targetModel = new TargetModel();

    // Map fields from source to target by matching field names/semantics
    targetModel.setFieldA(sourceModel.getFieldA());
    targetModel.setFieldB(sourceModel.getFieldB());
    // ... all mappable fields

    // also create corrosponding methods for inner nested objects like so:
    sourceModel.getListItems().foreach(listItem -> {
      targetModel.getItems().add(createTargetModelItem(listItem));
    })

    return targetModel;
}

private TargetModelItem createTargetModelItem(SourceModelItem sourceModelItem) {}
```

## Mapping Rules (Priority Order)

Field mapping follows this priority order:

1. **Paper mapping (highest priority)**: If a **paper-mapping** document is provided, look up each target field there first. Use the mapping rule from the paper mapping document. Only if a field is not covered by the paper mapping, fall through to the next step.
2. **Name similarity**: If no paper mapping is provided, or the field is not found in the paper mapping, match fields by name similarity. If source has `getOrderNumber()` and target has `setOrdernr()`, map them together. Use your best judgment to match semantically similar field names.
3. **Unmapped fields (TODO)**: If neither paper mapping nor name similarity yields a match, add a TODO comment with a default empty/null value:
  ```java
  // TODO: map unfoundFieldname
  targetModel.setUnfoundFieldname("");
  ```
  Use `""` for String fields, `null` for object/complex types.

### Type Compatibility
- Ensure type compatibility between source and target. If types differ, add a conversion (e.g., `String.valueOf()`, `.toString()`, parsing, etc.).

### Nested Objects
- If the target has nested objects (like `Orders.Order.OrderLine`), generate separate private methods for each nested mapping, following the same pattern.

### Collections/Lists
- If the target contains lists of child objects, generate a loop or stream that maps each child using a dedicated private `create` method.

### BigDecimal Fields
- Prefer a 2 decimal scale with `RoundingMode.HALF_UP`. Use `.toPlainString()` with a null check:
  ```java
  final String value = sourceModel.getValue() != null ? 
      sourceModel.getValue().setScale(2, RoundingMode.HALF_UP).toPlainString() 
      : "";
  ```

### Date Fields
- Use `DateTimeFormatter.ISO_DATE` for date fields and `DateTimeFormatter.ISO_DATE_TIME` for datetime fields, unless the paper mapping specifies a different format (e.g., zoned times).

### Paper Mapping Data Conversions
- If the paper mapping specifies data conversion logic (e.g., value lookups like `A -> 1, B -> 2, C -> 3`), create a dedicated private method for that conversion.
- Simple one-line String joins or format combinations (e.g., `String.join()`, `String.format()`) can be done inline in a local variable before the setter call, for readability.
- **If a lookup, conversion, join, or other logical rule from the paper mapping is not 100% clear, DO NOT ASSUME.** Instead, leave a TODO comment for the field with an explanation of why the logic was unclear:
  ```java
  // TODO: paper mapping specifies conversion for fieldName but the rule is ambiguous: "<quote the unclear rule>"
  targetModel.setFieldName("");
  ```

## Output Format

1. **Show the generated method(s)** as a complete code block with proper imports listed above it.
2. **List any unmapped fields** from both source and target so the developer knows what was skipped.
3. **Ask the developer** where they want the method placed (which class/file) or if they want a new Mapper class created.

## Important

- **Do NOT add code explanation comments.** No inline comments describing what a line does, no Javadoc, no section dividers. The logic is simple field mapping and self-explanatory. The only allowed comments are `// TODO` for unmapped fields.
- **Do NOT add any business logic.** Only map fields that have a clear and obvious relationship to each other (by name or type). Do not invent transformations, concatenations, formatting, or conditional logic. If the mapping is not straightforward, skip the field.
- **Do NOT create a full Mapper class** unless the user asks for it. Just generate the method(s).
- **Do NOT add Spring annotations** (`@Component`, `@Service`). Mappers in this codebase are plain beans.
- Keep the code simple and direct. Dont asume if no matches are found inthe paper mapping or field names. And dont asume or create complex logic.
- Follow the existing codebase style: use `final` for local variables, use SLF4J Logger if logging is needed.
- Make **`null` save** and **memory save** code, you can use functions from libraries for this **IF** they are already added in the `pom.xml`. For example, `commons-io` or `commons-lang3` are often available. When these libraries are added in the pom, prefer to use their function instead of creating your own functions or logic.
