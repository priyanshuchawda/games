import matplotlib.pyplot as plt
import networkx as nx

def draw_flowchart():
    G = nx.DiGraph()
    
    # Nodes
    G.add_node("Lung Cancer Dataset")
    G.add_node("Data pre-processing")
    G.add_node("Pre-processing using resize function")
    G.add_node("Data Augmentation using tensorflow model")
    G.add_node("Feature extraction using CNN")
    G.add_node("SVM Classification Algorithm")
    G.add_node("CART classification Algorithm")
    G.add_node("Random Forest Classification Algorithm")
    G.add_node("Cancer Detection")
    
    # Edges
    G.add_edges_from([
        ("Lung Cancer Dataset", "Data pre-processing"),
        ("Data pre-processing", "Pre-processing using resize function"),
        ("Pre-processing using resize function", "Data Augmentation using tensorflow model"),
        ("Data Augmentation using tensorflow model", "Feature extraction using CNN"),
        ("Feature extraction using CNN", "Data pre-processing"),
        ("Data pre-processing", "SVM Classification Algorithm"),
        ("Data pre-processing", "CART classification Algorithm"),
        ("Data pre-processing", "Random Forest Classification Algorithm"),
        ("SVM Classification Algorithm", "Cancer Detection"),
        ("CART classification Algorithm", "Cancer Detection"),
        ("Random Forest Classification Algorithm", "Cancer Detection")
    ])
    
    # Positioning
    pos = {
        "Lung Cancer Dataset": (4, 6),
        "Data pre-processing": (4, 5),
        "Pre-processing using resize function": (2, 4),
        "Data Augmentation using tensorflow model": (4, 4),
        "Feature extraction using CNN": (6, 4),
        "SVM Classification Algorithm": (2, 2),
        "CART classification Algorithm": (4, 2),
        "Random Forest Classification Algorithm": (6, 2),
        "Cancer Detection": (4, 0),
    }
    
    plt.figure(figsize=(10, 6))
    nx.draw(G, pos, with_labels=True, node_size=4000, node_color='lightgray', edge_color='black', font_size=10, font_weight='bold', arrows=True)
    plt.title("Lung Cancer Detection Flowchart")
    plt.show()

# Call the function
draw_flowchart()
