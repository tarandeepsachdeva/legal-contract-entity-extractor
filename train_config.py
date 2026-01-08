import spacy
from spacy.training.example import Example
from spacy.util import minibatch, compounding
import random
from pathlib import Path

def train_config():
    # Load config
    nlp = spacy.blank("en")
    
    # Add components manually with optimized settings
    nlp.add_pipe("sentencizer")
    ner = nlp.add_pipe("ner")
    
    # Load training data
    from spacy.tokens import DocBin
    db = DocBin().from_disk("data/annotation/NER/spacy/train.spacy")
    docs = list(db.get_docs(nlp.vocab))
    
    # Load validation data
    try:
        db_val = DocBin().from_disk("data/annotation/NER/spacy/val.spacy")
        val_docs = list(db_val.get_docs(nlp.vocab))
    except:
        val_docs = docs[:5]  # Use first 5 as validation if no val data
    
    # Add labels
    for doc in docs:
        for ent in doc.ents:
            ner.add_label(ent.label_)
    
    print(f"Training on {len(docs)} docs, validating on {len(val_docs)} docs")
    print(f"Labels: {ner.labels}")
    
    # Initialize with examples
    train_examples = []
    for doc in docs:
        try:
            example = Example.from_dict(
                nlp.make_doc(doc.text),
                {"entities": [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]}
            )
            train_examples.append(example)
        except:
            continue
    
    # Initialize pipeline
    nlp.initialize(get_examples=lambda: train_examples)
    
    # Training loop with better parameters
    optimizer = nlp.create_optimizer()
    
    best_score = 0
    patience = 10
    patience_counter = 0
    
    for epoch in range(80):  # More epochs
        random.shuffle(train_examples)
        losses = {}
        
        # Use smaller batches with compounding schedule
        batches = minibatch(train_examples, size=compounding(4.0, 32.0, 1.001))
        
        for batch in batches:
            nlp.update(batch, sgd=optimizer, losses=losses, drop=0.3)
        
        # Evaluate every 10 epochs
        if epoch % 10 == 0:
            scores = evaluate_model(nlp, val_docs)
            print(f"Epoch {epoch+1} | Loss: {losses.get('ner', 0):.2f} | F1: {scores.get('ents_f', 0):.3f}")
            
            # Early stopping
            if scores.get('ents_f', 0) > best_score:
                best_score = scores.get('ents_f', 0)
                patience_counter = 0
                # Save best model
                output_dir = Path("training_output/best_model")
                output_dir.mkdir(parents=True, exist_ok=True)
                nlp.to_disk(output_dir)
                print(f"  New best model saved! F1: {best_score:.3f}")
            else:
                patience_counter += 1
                
            if patience_counter >= patience:
                print(f"Early stopping at epoch {epoch+1}")
                break
        else:
            print(f"Epoch {epoch+1} | Loss: {losses.get('ner', 0):.2f}")
    
    # Save final model
    output_dir = Path("training_output/config_model")
    output_dir.mkdir(parents=True, exist_ok=True)
    nlp.to_disk(output_dir)
    print(f"✅ Final model saved to {output_dir}")

def evaluate_model(nlp, val_docs):
    """Simple evaluation function"""
    val_examples = []
    for doc in val_docs:
        try:
            example = Example.from_dict(
                nlp.make_doc(doc.text),
                {"entities": [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]}
            )
            val_examples.append(example)
        except:
            continue
    
    if val_examples:
        scorer = nlp.evaluate(val_examples)
        return scorer
    else:
        return {"ents_f": 0.0}

if __name__ == "__main__":
    train_config()
