package br.ufpe.cin.main;

import com.github.javaparser.JavaParser;
import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.URI;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.SimpleFileVisitor;
import java.nio.file.StandardOpenOption;
import java.util.List;


import org.antlr.v4.runtime.ANTLRInputStream;
import org.antlr.v4.runtime.Token;
import edu.wm.cs.compiler.tools.generators.scanners.JavaLexer;

public class ExtractMethod extends SimpleFileVisitor<Path> {

    //private static final String FILE_PATH = "java-parser/src/main/resources/OTFSubSetFile.java-2-Extract Method-37-writeTopDICT";

    public static void main(String[] args) throws Exception {

        
        if(args.length < 1) {
			throw new IllegalArgumentException("Not enough arguments!");
        }
        
        
        String FILE_PATH_BEFORE = args[0];  
        //String FILE_PATH_BEFORE = "/home/r4ph/desenv/projetos/Data-Collection/storage/PermissionsDispatcher/579058/before/CallOnRequestPermissionsResultDetector.java"; 
               
        String FILE_PATH_AFTER = args[1];  
        //String FILE_PATH_AFTER = "/home/r4ph/desenv/projetos/Data-Collection/storage/PermissionsDispatcher/579058/after/CallOnRequestPermissionsResultDetector.java"; 
         
        String OUTPUT_PATH_BEFORE = args[2]; 
        //final String OUTPUT_PATH_BEFORE = "data/raw/_example/example_before.java";

        String OUTPUT_PATH_AFTER = args[3]; 
        //final String OUTPUT_PATH_AFTER = "data/raw/_example/example_after.java";
        
        String IDIOMS_PATH_BEFORE = args[4]; 
        //String IDIOMS_PATH_BEFORE = "data/raw/_idioms/raw_idioms_before.txt";

        String IDIOMS_PATH_AFTER = args[5]; 
        //String IDIOMS_PATH_AFTER = "data/raw/_idioms/raw_idioms_after.txt";
        
        String METHOD_NAME = args[6]; 
        //String METHOD_NAME = "visitMethod";
        //String[] FILES = {FILE_BEFORE_PATH,FILE_AFTER_PATH};  

        String ID = args[7];  
            
        CompilationUnit cu_before = StaticJavaParser.parse(new FileInputStream(FILE_PATH_BEFORE));

        cu_before.accept(new VoidVisitorAdapter<Void>() {

            /**
             * For every if-statement, see if it has a comparison using "!=". Change it to
             * "==" and switch the "then" and "else" statements around.
             * 
             * @return
             */
            @Override
            public void visit(MethodDeclaration md, Void arg) {

                String methodName = METHOD_NAME; //FILE_PATH.substring(FILE_PATH.lastIndexOf("-") + 1).replace(".java", "");
                if (methodName.equals(md.getName().toString())) {
                    //System.out.println("Method Before Extracted from File: " + methodName);
                    //System.out.println("* Method is Equals! *: " + md.getName());
                    //System.out.println(" * Position * " + md.getBegin());
                    //System.out.println(" * Body * " + md.getBody());
                    //System.out.println(" * Declaration * " + md.getDeclarationAsString());
                    String extractedMethod = md.getDeclarationAsString().concat(md.getBody().stream().findFirst().get().toString());
                    // System.out.println(" * Extracted Method * " + extractedMethod);
                    // outputPath = concat(new File(FILE_PATH).getParent())
                    // String outputPath = FILE_PATH.concat("-Extracted");
                    //String extractedMethodFormated = extractedMethod.replaceAll("\n", " ").trim().replaceAll("\\s{2,}", " ");
                    //System.out.println(" * Extracted Method * " + extractedMethodFormated);

                    //InputStream inputStream = new FileInputStream(extractedMethod.toString());
                    JavaLexer jLexer = new JavaLexer(new ANTLRInputStream(extractedMethod));
                        
                    StringBuilder sb = new StringBuilder();
                    StringBuilder sb_total = new StringBuilder();
                    Integer sb_counter = 0;
                    
                    for (Token t = jLexer.nextToken(); t.getType() != Token.EOF; t = jLexer.nextToken()) {
                        String token = "";
                        if(t.getType() == JavaLexer.Identifier) {
                            //System.out.println(" Identifier: "+ t.getText());	
                            token = t.getText();
                            sb.append(token + " ");
                            //token = getIdentifierID(t);

                        }else if(t.getType() == JavaLexer.CharacterLiteral | t.getType() == JavaLexer.FloatingPointLiteral | t.getType() == JavaLexer.IntegerLiteral | t.getType() == JavaLexer.StringLiteral) {
                            //System.out.println(" Literal: "+ t.getText());
                            token = t.getText();	
                            sb.append(token + " ");
                        } else {
                            //System.out.println(" Other: "+ t.getText());	
                            //token = t.getText();
                        }
                        sb_total.append(token + " ");
                    }
                    
                    sb_counter = sb_total.toString().split(" ").length;
                    //System.out.println("Quantidade Total de Tokens: "+ sb_counter.toString());

                    try {
                        Files.write(Paths.get(OUTPUT_PATH_BEFORE), extractedMethod.getBytes());
                        String s = System.lineSeparator() + ID + " " + sb_counter.toString() + " " + sb.toString();
                        Files.write(Paths.get(IDIOMS_PATH_BEFORE), s.getBytes(), StandardOpenOption.APPEND);
                    } catch (IOException e) {
                        System.out.println("### Erro na Tokenização do Método (Before): " + METHOD_NAME + e);
                        e.printStackTrace();
                    }
    

                    
                }
            }
        }, null);

        //File After Refactoring

        CompilationUnit cu_after = StaticJavaParser.parse(new FileInputStream(FILE_PATH_AFTER));

        cu_after.accept(new VoidVisitorAdapter<Void>() {

            /**
             * For every if-statement, see if it has a comparison using "!=". Change it to
             * "==" and switch the "then" and "else" statements around.
             * 
             * @return
             */
            @Override
            public void visit(MethodDeclaration md, Void arg) {

                String methodName = METHOD_NAME; //FILE_PATH.substring(FILE_PATH.lastIndexOf("-") + 1).replace(".java", "");
                if (methodName.equals(md.getName().toString())) {
                    //System.out.println("Method After Extracted from File: " + methodName);
                    //System.out.println("* Method is Equals! *: " + md.getName());
                    //System.out.println(" * Position * " + md.getBegin());
                    //System.out.println(" * Body * " + md.getBody());
                    //System.out.println(" * Declaration * " + md.getDeclarationAsString());
                    String extractedMethod = md.getDeclarationAsString().concat(md.getBody().stream().findFirst().get().toString());
                    // System.out.println(" * Extracted Method * " + extractedMethod);
                    // outputPath = concat(new File(FILE_PATH).getParent())
                    // String outputPath = FILE_PATH.concat("-Extracted");
                    //String extractedMethodFormated = extractedMethod.replaceAll("\n", " ").trim().replaceAll("\\s{2,}", " ");
                    //System.out.println(" * Extracted Method * " + extractedMethodFormated);

                    //InputStream inputStream = new FileInputStream(extractedMethod.toString());
                    JavaLexer jLexer = new JavaLexer(new ANTLRInputStream(extractedMethod));
                        
                    StringBuilder sb = new StringBuilder();
                    StringBuilder sb_total = new StringBuilder();
                    Integer sb_counter = 0;
                    
                    for (Token t = jLexer.nextToken(); t.getType() != Token.EOF; t = jLexer.nextToken()) {
                        String token = "";
                        if(t.getType() == JavaLexer.Identifier) {
                            //System.out.println(" Identifier: "+ t.getText());	
                            token = t.getText();
                            sb.append(token + " ");
                            //token = getIdentifierID(t);

                        }else if(t.getType() == JavaLexer.CharacterLiteral | t.getType() == JavaLexer.FloatingPointLiteral | t.getType() == JavaLexer.IntegerLiteral | t.getType() == JavaLexer.StringLiteral) {
                            //System.out.println(" Literal: "+ t.getText());
                            token = t.getText();	
                            sb.append(token + " ");
                        } else {
                            //System.out.println(" Other: "+ t.getText());	
                            //token = t.getText();
                        }
                        sb_total.append(token + " ");
                    }
                    
                    sb_counter = sb_total.toString().split(" ").length;
                    //System.out.println("Quantidade Total de Tokens: "+ sb_counter.toString());

                    try {
                        Files.write(Paths.get(OUTPUT_PATH_AFTER), extractedMethod.getBytes());
                        String s = System.lineSeparator() + ID + " " + sb_counter.toString() + " " + sb.toString();
                        Files.write(Paths.get(IDIOMS_PATH_AFTER), s.getBytes(), StandardOpenOption.APPEND);
                    } catch (IOException e) {
                        System.out.println("### Erro na Tokenização do Método (After): " + METHOD_NAME + e);
                        e.printStackTrace();
                    }
    

                    
                }
            }
        }, null);
            
             
        //VoidVisitor<?> methodNameVisitor = new MethodNamePrinter();
        //methodNameVisitor.visit(cu, null); 
        //List<String> methodNames = new ArrayList<>();
        //VoidVisitor<List<String>> methodNameCollector = new MethodNameCollector();
        //methodNameCollector.visit(cu, methodNames);
        //methodNames.forEach(n -> System.out.println("Method Name Collected: " + n));

    }

    // private static class MethodNamePrinter extends VoidVisitorAdapter<Void> {

    //     @Override
    //     public void visit(MethodDeclaration md, Void arg) {
    //         super.visit(md, arg);
    //         String methodName = FILE_PATH.substring(FILE_PATH.lastIndexOf("-") + 1).replace(".java", "");
    //         System.out.println("Method Name Extracted from File: " + methodName);
    //         if (methodName.equals(md.getName().toString())) {
    //             System.out.println("* Method is Equals! *: " + md.getName());
    //             System.out.println(" * Position * " + md.getBegin());
    //             System.out.println(" * Body * " + md.getBody());
    //             System.out.println(" * Declaration * " + md.getDeclarationAsString());
    //             String extractedMethod = md.getDeclarationAsString()
    //                     .concat(md.getBody().stream().findFirst().get().toString());
    //             System.out.println(" * Extracted Method * " + extractedMethod);
    //             // outputPath = concat(new File(FILE_PATH).getParent())
    //             String outputPath = FILE_PATH.concat("-Extracted");
    //             try {
    //                 Files.write(Paths.get(outputPath), extractedMethod.getBytes());
    //             } catch (IOException e) {
    //                 e.printStackTrace();
    //             }
    //         }
    //     }
    // }

    private static class MethodNameCollector extends VoidVisitorAdapter<List<String>> {

        @Override
        public void visit(MethodDeclaration md, List<String> collector) {
            super.visit(md, collector);
            collector.add(md.getNameAsString());
        }
    }

}