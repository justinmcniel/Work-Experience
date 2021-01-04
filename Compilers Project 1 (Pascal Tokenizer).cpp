#include <iostream>
#include <string.h>
#include <stdlib.h>
#include <math.h>

using namespace std;

///DOES NOT PROCESS IN THE ORDER THEY'RE ASSIGNED, PROCESSES IN PRECEDENCE, THEN COMMONALITY
//Tokens
#define ADDOP     10
#define MULOP     11
#define COLN      12
#define OPAREN    13
#define CPAREN    14
#define COMMA     15
#define SEMICOLN  16
#define PERIOD    17
#define OBRACK    18
#define CBRACK    19
#define OBRACE    20
#define CBRACE    21
#define EOFval    22
#define INT       23
#define REAL      24
#define LONGREAL  24    ///he said that the combo for this is (NUM REAL)
#define NUM       25
#define ID        26
#define NEWLINE   27
#define RELOP     28
#define ASSIGNOP  29
#define PROG      30
#define VAR       31
#define ARRAY     32
#define OF        33
#define FUNC      34
#define PROCEDURE 35
#define BEGIN     36
#define END       37
#define IF        38
#define THEN      39
#define ELSE      40
#define WHILE     41
#define DO        42
#define NOT       43

///RULES FOR PROCESSING ARE SAME AS FOR THE TOKENS
//Attributes
#define ADD       10
#define SUB       11
#define MUL       12
#define DIVIDE    13
#define EQ        14
#define NEQ       15
#define LT        16
#define GT        17
#define LEQ       18
#define GEQ       19
#define OR        20
#define DIV       21
#define MOD       22
#define AND       23
#define ASSIGN    24

//errors
#define LEXERR                  0b10000000 //Is a token, not an attribute modifier
#define UNRECOGNIZED_SYMBOL_ERR 0b0100000000000000
#define UNEXPECTED_SYMBOL_ERR   0b0010000000000000 //not used
#define ID_TOO_LONG             0b0001000000000000
#define INT_TOO_LONG            0b0000100000000000
#define LEX2_TOO_LONG           0b0000010000000000
#define LEX1_TOO_LONG           0b0000001000000000
#define LEX0_TOO_LONG           0b0000000100000000
#define LEADING00_ERR           0b0000000010000000
#define LEADING02_ERR           0b0000000001000000

void output(char *str)
{
    FILE *listing_file = fopen("listing.txt", "a");

    fputs((const char*)str, listing_file);

    fclose(listing_file);

    printf((const char*) str);
}

struct Symbol
{
    char *lexeme;
    char *token_lexeme;
    int   token;
    char *attribute_lexeme;
    int   attribute;
};

struct SymbolListNode
{
    Symbol *symbol;
    SymbolListNode *nxt = nullptr;
};

struct SymbolList
{
    SymbolListNode *head = nullptr;
};

Symbol *findSymbol(SymbolList *lst, Symbol *item)
{
    SymbolListNode *next_symbol = lst->head;

    Symbol *res = nullptr;

    while(next_symbol != nullptr)
    {
        Symbol *symbl = next_symbol->symbol;

        if(strcmp((const char*)item->lexeme, (const char*)symbl->lexeme) == 0 &&
           strcmp((const char*)item->token_lexeme, (const char*)symbl->token_lexeme) == 0 &&
           strcmp((const char*)item->attribute_lexeme, (const char*)symbl->attribute_lexeme) == 0 &&
           item->token == symbl->token &&
           item->attribute == symbl->attribute)
        {
            res = symbl;
            break;
        }

        next_symbol = next_symbol->nxt;
    }

    return res;
}

void appendSymbol(SymbolList *lst, Symbol *item)
{
    SymbolListNode *next_symbol = lst->head;

    if(next_symbol == nullptr)
    {
        SymbolListNode *new_node = (SymbolListNode*)malloc(sizeof(SymbolListNode));
        lst->head = new_node;
        lst->head->nxt = nullptr;
        lst->head->symbol = item;
        return;
    }

    SymbolListNode *current = nullptr;

    while(next_symbol != nullptr)
    {
        current = next_symbol;
        next_symbol = next_symbol->nxt;
    }

    SymbolListNode *new_node = (SymbolListNode*)malloc(sizeof(SymbolListNode));
    current->nxt = new_node;
    new_node->nxt = nullptr;
    new_node->symbol = item;
    return;
}

struct ReservedWord
{
    char *lexeme;
    int   token;
    int   attribute;
};

struct ReservedWordListNode
{
    ReservedWord *reserved_word;
    ReservedWordListNode *nxt = nullptr;
};

struct ReservedWordList
{
    ReservedWordListNode *head = nullptr;
};

ReservedWord *findWord(ReservedWordList *lst, ReservedWord *item)
{
    ReservedWordListNode *next_word = lst->head;

    ReservedWord *res = nullptr;

    while(next_word != nullptr)
    {
        ReservedWord *wrd = next_word->reserved_word;

        if(strcmp((const char*)item->lexeme, (const char*)wrd->lexeme) == 0 &&
           item->token == wrd->token &&
           item->attribute == wrd->attribute)
        {
            res = wrd;
            break;
        }

        next_word = next_word->nxt;
    }

    return res;
}

void appendWord(ReservedWordList *lst, ReservedWord *item)
{
    ReservedWordListNode *next_word = lst->head;

    if(next_word == nullptr)
    {
        ReservedWordListNode *new_node = (ReservedWordListNode*)malloc(sizeof(ReservedWordListNode));
        lst->head = new_node;
        lst->head->nxt = nullptr;
        lst->head->reserved_word = item;
        return;
    }

    ReservedWordListNode *current = nullptr;

    while(next_word != nullptr)
    {

        current = next_word;
        next_word = next_word->nxt;
    }

    ReservedWordListNode *new_node = (ReservedWordListNode*)malloc(sizeof(ReservedWordListNode));
    current->nxt = new_node;
    new_node->nxt = nullptr;
    new_node->reserved_word = item;
    return;
}

bool isnum(char x)
{
    return  x == '1' || x == '2' || x == '3' || x == '4' || x == '5' ||
            x == '6' || x == '7' || x == '8' || x == '9' || x == '0';
}

bool isalph(char x)
{
    return  x == 'a' || x == 'b' || x == 'c' || x == 'd' || x == 'e' ||
            x == 'f' || x == 'g' || x == 'h' || x == 'i' || x == 'j' ||
            x == 'k' || x == 'l' || x == 'm' || x == 'n' || x == 'o' ||
            x == 'p' || x == 'q' || x == 'r' || x == 's' || x == 't' ||
            x == 'u' || x == 'v' || x == 'w' || x == 'x' || x == 'y' ||
            x == 'z' || x == 'A' || x == 'B' || x == 'C' || x == 'D' ||
            x == 'E' || x == 'F' || x == 'G' || x == 'H' || x == 'I' ||
            x == 'J' || x == 'K' || x == 'L' || x == 'M' || x == 'N' ||
            x == 'O' || x == 'P' || x == 'Q' || x == 'R' || x == 'S' ||
            x == 'T' || x == 'U' || x == 'V' || x == 'W' || x == 'X' ||
            x == 'Y' || x == 'Z';
}

bool isalphnum(char x)
{
    return  isnum(x) || isalph(x);
}

///write to listing file as we progress
int main(int argc, char **argv)
{
    char *tmp = (char*)malloc(72);
    char *tmp0 = (char*)malloc(72);

    {//empties listing file
        FILE *listing_file = fopen("listing.txt", "w");

        tmp[0] = '\0';
        fputs((const char*)tmp, listing_file);

        fclose(listing_file);
    }

    /*
    Open the files
    */
    FILE *source_code = fopen("source1.txt", "r");
    FILE *token_file = fopen("tokens.txt", "w");
    FILE *symbol_table_file = fopen("symbols.txt", "w");

    ReservedWordList *reserved_words = (ReservedWordList*)malloc(sizeof(ReservedWordList));
    reserved_words->head = nullptr;
    FILE *reserved_word_file = fopen("reservedwords.txt", "r");

    while(true)
    {
        char* fgetsres = fgets(tmp, 72, (FILE*)reserved_word_file);

        if(tmp[0] == '\0' || fgetsres == nullptr)//the line was empty
        {
            break;
        }

        int stage = 0;

        ReservedWord *tmpword = (ReservedWord*)malloc(sizeof(ReservedWord));
        int place = 0;

        for(int i = 0; i < 72; i++)
        {
            if(tmp[i] == '\t' || tmp[i] == ' ' || tmp[i] == '\n')
            {
                switch(stage)
                {
                case 0:
                    tmp0 = tmp;
                    tmp0[i] = '\0';
                    tmpword->lexeme = (char*)malloc(strlen(tmp0));
                    strcpy(tmpword->lexeme, tmp0);
                    stage++;
                    place = i+1;
                    break;
                case 1:
                    tmpword->token = atoi(&(tmp[place]));
                    stage++;
                    place = i+1;
                    break;
                case 2:
                    tmpword->attribute = atoi(&(tmp[place]));
                    stage++;
                    place = i+1;
                    break;
                default:
                    //Error
                    break;
                }
                while(tmp[i] == '\t' || tmp[i] == ' ' || tmp[i] == '\n')
                {
                    i++;
                }
            }
        }

        appendWord(reserved_words, tmpword);
    }

    fclose(reserved_word_file);
    //reserved words loading correctly

    SymbolList *symbols = (SymbolList*)malloc(sizeof(SymbolList));
    symbols->head = nullptr;

    //optionally read line here, and at end of loop, and check condition in loop header
    int line = 1;
    char *codeline = (char*)malloc(72);
    bool EOFHit = false;

    while(!EOFHit)
    {

        //read line to c string
        char* fgetsres = fgets(codeline, 72, (FILE*)source_code);

        int f = 0;
        int b = 0;
        bool wasWhitespace;
        int token;
        int attribute;
        char *lexeme;

        if(fgetsres == nullptr)
        {
            //if you hit the EOF
            EOFHit = true;
            codeline[0] = '\0';
            lexeme = (char*)malloc(72);
            goto EOFHandler;
        }

        itoa(line, tmp, 10);
        if(line != 1){output((const char*)"\n");}
        output(tmp);
        output((const char*)"\t");
        output(codeline);
        if(codeline[strlen(codeline)-1] != '\n'){output((const char*)"\n");}

        while(b < (int)strlen(codeline)) ///make sure this is the right comparison
        {
            token = LEXERR;
            attribute = (int)NULL;
            lexeme = (char*)malloc(72);

            f = b;
            ///ID RES
            if(isalph(codeline[f]))
            {
                lexeme[0] = codeline[f];
                int spot = 1;
                f++;
                while(isalph(codeline[f]) | isdigit(codeline[f]))
                {
                    lexeme[spot] = codeline[f];
                    spot++;
                    f++;
                }
                lexeme[spot] = '\0';

                ///assumes that there is at least 1 reserved word, it would be an interesting language if there weren't
                ReservedWordListNode *word = reserved_words->head;
                do
                {

                    if(strcmp((const char*)lexeme, (const char*)word->reserved_word->lexeme) == 0)
                    {
                        attribute = word->reserved_word->attribute;
                        token = word->reserved_word->token;
                        break;
                    }
                }while((word = word->nxt) != nullptr);

                if(token == LEXERR)
                {
                    SymbolListNode *symbol = symbols->head;

                    if(symbol != nullptr)
                    {
                        do
                        {
                            if(strcmp((const char*)lexeme, (const char*)symbol->symbol->lexeme) == 0)
                            {
                                attribute = symbol->symbol->attribute;
                                token = symbol->symbol->token;
                                break;
                            }
                        }while((symbol = symbol->nxt) != nullptr);
                    }

                    if(token == LEXERR) // if it's a new symbol
                    {
                        token = ID;
                        Symbol *new_symb = (Symbol*)malloc(sizeof(Symbol));
                        new_symb->attribute = (int)NULL;///?
                        new_symb->token = ID;
                        new_symb->lexeme = (char*)malloc(strlen(lexeme));
                        strcpy(new_symb->lexeme, lexeme);
                    }
                }
            }

            if(token != LEXERR)
            {
                goto SaveLexeme;
            }

            f = b;
            ///Whitespace
            wasWhitespace = false;
            while(codeline[f] == ' ' || codeline[f] == '\t')
            {
                f++;
                wasWhitespace = true;
            }
            b = f;
            if(wasWhitespace)
            {
                continue;
            }

            if(token != LEXERR)
            {
                goto SaveLexeme;
            }

            f = b;
            ///catchall
            lexeme[1] = '\0';
            if(codeline[f] == '+')
            {
                f++;
                token = ADDOP;
                attribute = ADD;
                lexeme[0] = '+';
            }
            else if(codeline[f] == '-')
            {
                f++;
                token = ADDOP;
                attribute = SUB;
                lexeme[0] = '-';
            }
            else if(codeline[f] == '*')
            {
                f++;
                token = MULOP;
                attribute = MUL;
                lexeme[0] = '*';
            }
            else if(codeline[f] == '/')
            {
                f++;
                token = MULOP;
                attribute = DIVIDE;
                lexeme[0] = '/';
            }
            else if(codeline[f] == ':')
            {
                lexeme[0] = ':';
                f++;
                if(codeline[f] == '=')
                {
                    f++;
                    token = ASSIGNOP;
                    attribute = ASSIGN;
                    lexeme[1] = '=';
                    lexeme[2] = '\0';
                }
                else
                {
                    token = COLN;
                    attribute = (int)NULL;
                }
            }
            else if(codeline[f] == '(')
            {
                f++;
                token = OPAREN;
                attribute = (int)NULL;
                lexeme[0] = '(';
            }
            else if(codeline[f] == ')')
            {
                f++;
                token = CPAREN;
                attribute = (int)NULL;
                lexeme[0] = ')';
            }
            else if(codeline[f] == ',')
            {
                f++;
                token = COMMA;
                attribute = (int)NULL;
                lexeme[0] = ',';
            }
            else if(codeline[f] == ';')
            {
                f++;
                token = SEMICOLN;
                attribute = (int)NULL;
                lexeme[0] = ';';
            }
            else if(codeline[f] == '.')
            {
                f++;
                token = PERIOD;
                attribute = (int)NULL;
                lexeme[0] = '.';
            }
            else if(codeline[f] == '[')
            {
                f++;
                token = OBRACK;
                attribute = (int)NULL;
                lexeme[0] = '[';
            }
            else if(codeline[f] == ']')
            {
                f++;
                token = CBRACK;
                attribute = (int)NULL;
                lexeme[0] = ']';
            }
            else if(codeline[f] == '\n')
            {
                f++;
                token = NEWLINE;
                attribute = (int)NULL;
                lexeme[0] = '\\';
                lexeme[1] = 'n';
                lexeme[2] = '\0';
            }
            else if(codeline[f] == 0x05) //5 is the ASCII code for EOF
            {
                f++;
                EOFHandler:
                EOFHit = true;
                token = EOFval;
                attribute = (int)NULL;

                lexeme[0] = 'E';
                lexeme[1] = 'O';
                lexeme[2] = 'F';
                lexeme[3] = '\0';
            }
            else
            {
                token = LEXERR;
            }

            if(token != LEXERR)
            {
                goto SaveLexeme;
            }

            f = b;
            ///longreal
            if(!isnum(codeline[f]))
            {
                token = LEXERR;
            }
            else
            {
                token = NUM;
                attribute = LONGREAL;

                bool exp_is_neg = false;

                char *lex0 = (char*)malloc(72);

                lex0[0] = codeline[f];

                int spot = 1;
                f++;

                while(isnum(codeline[f]))
                {
                    lex0[spot] = codeline[f];
                    f++;
                    spot++;
                }

                lex0[spot] = '\0'; //puts the null character at the end of the number to denote the end of the string

                if(codeline[f] != '.')
                {
                    token = LEXERR;
                    f = b;
                }
                else
                {
                    f++;
                    if(!isnum(codeline[f]))
                    {
                        attribute = attribute | UNEXPECTED_SYMBOL_ERR;
                        //output((const char*)"LEXERR:\tUnexpected Symbol:\t");
                        tmp[0] = codeline[f];
                        tmp[1] = '\0';
                        //output(tmp);
                        //output((const char*)"\n"); ///it should be implicitly done in the real machine after this
                        token = LEXERR;
                        f = b;
                    }
                    else
                    {
                        char *lex1 = (char*)malloc(72);

                        lex1[0] = codeline[f];

                        spot = 1;
                        f++;

                        while(isnum(codeline[f]))
                        {
                            lex1[spot] = codeline[f];
                            f++;
                            spot++;
                        }

                        lex1[spot] = '\0'; //puts the null character at the end of the number to denote the end of the string

                        if(codeline[f] != 'E')
                        {
                            token = LEXERR;
                            f = b;
                        }
                        else
                        {
                            f++;

                            if(codeline[f] == '+')
                            {
                                f++; //don't bother notating this, it won't change the value
                            }
                            else if(codeline[f] == '-')
                            {
                                f++;
                                exp_is_neg = true;
                            }

                            if(!isnum(codeline[f]))
                            {
                                attribute = attribute | UNEXPECTED_SYMBOL_ERR;
                                output((const char*)"LEXERR:\tUnexpected Symbol:\t");
                                tmp[0] = codeline[f];
                                tmp[1] = '\0';
                                output(tmp);
                                output((const char*)"\n");
                                token = LEXERR;
                                f = b;
                            }
                            else
                            {
                                char *lex2 = (char*)malloc(72);

                                lex2[0] = codeline[f];

                                spot = 1;
                                f++;

                                while(isnum(codeline[f]))
                                {
                                    lex2[spot] = codeline[f];
                                    f++;
                                    spot++;
                                }

                                lex2[spot] = '\0'; //putting a null character after the number to denote the end of the string

                                if(strlen(lex0) > 5)
                                {
                                    attribute = attribute | LEX0_TOO_LONG;
                                    output((const char*)"LEXERR:\tExtra Long Integer Part:\t");
                                    output(lex0);
                                    output((const char*)"\n");
                                    //token = LEXERR;
                                }

                                if(strlen(lex1) > 5)
                                {
                                    attribute = attribute | LEX1_TOO_LONG;
                                    output((const char*)"LEXERR:\tExtra Long Fractional Part:\t");
                                    output(lex1);
                                    output((const char*)"\n");
                                    //token = LEXERR;
                                }

                                if(strlen(lex2) > 2)
                                {
                                    attribute = attribute | LEX2_TOO_LONG;
                                    output((const char*)"LEXERR:\tExtra Long Exponent:\t");
                                    output(lex2);
                                    output("\n");
                                    //token = LEXERR;
                                }

                                if(lex0[0] == '0' && strlen(lex0) > 1)
                                {
                                    attribute = attribute | LEADING00_ERR;
                                    output((const char*)"LEXERR:\tLeading Zero on Non-Zero Integer Part:\t");
                                    output(lex0);
                                    output("\n");
                                }

                                if(lex2[0] == '0' && strlen(lex2) > 1)
                                {
                                    attribute = attribute | LEADING02_ERR;
                                    output((const char*)"LEXERR:\tLeading Zero on Non-Zero Exponent Part:\t");
                                    output(lex2);
                                    output("\n");
                                }

                                ///TODO: store numbers here

                                for(int i = b; i < f; i++)
                                {
                                    lexeme[i-b] = codeline[i];
                                }

                                lexeme[f-b+1] = '\0';

                                free(lex2);
                                lex2 = nullptr;
                            }
                        }

                        free(lex1);
                        lex1 = nullptr;
                    }
                }


                free(lex0);
                lex0 = nullptr;

                b = f;
            }

            if(token != LEXERR)
            {
                goto SaveLexeme;
            }

            f = b;
            ///real
            if(!isnum(codeline[f]))
            {
                token = LEXERR;
            }
            else
            {
                token = NUM;
                attribute = REAL;

                char *lex0 = (char*)malloc(72);

                lex0[0] = codeline[f];

                int spot = 1;
                f++;

                while(isnum(codeline[f]))
                {
                    lex0[spot] = codeline[f];
                    f++;
                    spot++;
                }
                lex0[spot] = '\0'; //puts the null character at the end of the number to denote the end of the string

                if(codeline[f] != '.')
                {
                    token = LEXERR;
                    f = b;
                }
                else
                {
                    f++;
                    if(!isnum(codeline[f]))
                    {
                        attribute = attribute | UNEXPECTED_SYMBOL_ERR;
                        output((const char*)"LEXERR:\tUnexpected Symbol:\t");
                        tmp[0] = codeline[f];
                        tmp[1] = '\0';
                        output(tmp);
                        output("\n");
                        token = LEXERR;
                        f = b;
                    }
                    else
                    {
                        char *lex1 = (char*)malloc(72);

                        lex1[0] = codeline[f];

                        spot = 1;
                        f++;

                        while(isnum(codeline[f]))
                        {
                            lex1[spot] = codeline[f];
                            f++;
                            spot++;
                        }
                        lex1[spot] = '\0'; //puts the null character at the end of the number to denote the end of the string

                        if(strlen(lex0) > 5)
                        {
                            attribute = attribute | LEX0_TOO_LONG;
                            output((const char*)"LEXERR:\tExtra Long Integer Part:\t");
                            output(lex0);
                            output("\n");
                            //token = LEXERR;
                        }

                        if(strlen(lex1) > 5)
                        {
                            attribute = attribute | LEX1_TOO_LONG;
                            output((const char*)"LEXERR:\tExtra Long Fractional Part:\t");
                            output(lex1);
                            output("\n");
                            //token = LEXERR;
                        }

                        if(lex0[0] == '0' && strlen(lex0) > 1)
                        {
                            attribute = attribute | LEADING00_ERR;
                            output((const char*)"LEXERR:\tLeading Zero on Non-Zero Integer Part:\t");
                            output(lex0);
                            output("\n");
                        }

                        for(int i = b; i < f; i++)
                        {
                            lexeme[i-b] = codeline[i];
                        }

                        lexeme[f-b+1] = '\0';

                        ///TODO: Store num

                        for(int i = b; i < f; i++)
                        {
                            lexeme[i-b] = codeline[i];
                        }

                        lexeme[f-b+1] = '\n';

                        free(lex1);
                        lex1 = nullptr;
                    }
                }

                free(lex0);
                lex0 = nullptr;
            }

            if(token != LEXERR)
            {
                goto SaveLexeme;
            }

            f = b;
            ///int
            if(!isnum(codeline[f]))
            {
                token = LEXERR;
            }
            else
            {
                token = NUM;
                attribute = INT;

                lexeme[0] = codeline[f];

                int spot = 1;
                f++;

                while(isnum(codeline[f]))
                {
                    lexeme[spot] = codeline[f];
                    f++;
                    spot++;
                }
                lexeme[spot] = '\0'; //puts the null character at the end of the number to denote the end of the string
                if(strlen(lexeme) > 10)
                {
                    attribute = attribute | INT_TOO_LONG;
                    output((const char*)"LEXERR:\tExtra Long Integer:\t");
                    output(lexeme);
                    output("\n");
                    //token = LEXERR;
                }

                if(lexeme[0] == '0' && strlen(lexeme) > 1)
                {
                    attribute = attribute | LEADING00_ERR;
                    output((const char*)"LEXERR:\tLeading Zero on Non-Zero Integer Part:\t");
                    output(lexeme);
                    output("\n");
                }
            }

            if(token != LEXERR)
            {
                goto SaveLexeme;
            }

            f = b;
            ///relop
            lexeme[1] = '\0';
            lexeme[2] = '\0';
            if(codeline[f] == '=')
            {
                f++;
                token = RELOP;
                attribute = EQ;
                lexeme[0] = '=';
            }
            else if(codeline[f] == '<')
            {
                lexeme[0] = '<';
                f++;
                token = RELOP;
                if(codeline[f] == '>')
                {
                    lexeme[1] = '>';
                    f++;
                    attribute = NEQ;
                }
                else if(codeline[f] == '=')
                {
                    lexeme[1] = '=';
                    f++;
                    attribute = LEQ;
                }
                else
                {
                    attribute = LT;
                }
            }
            else if(codeline[f] == '>')
            {
                lexeme[0] = '>';
                f++;
                token = RELOP;
                if(codeline[f] == '=')
                {
                    lexeme[1] = '=';
                    f++;
                    attribute = GEQ;
                }
                else
                {
                    attribute = GT;
                }
            }



            if(token != LEXERR)
            {
                goto SaveLexeme;
            }

            //unrec symb err
            //token = LEXERR; should already be true
            attribute = UNRECOGNIZED_SYMBOL_ERR;
            output((const char*)"LEXERR:\tUnrecognized Symbol:\t");
            tmp[0] = codeline[f];
            tmp[1] = '\0';
            lexeme[0] = codeline[f];
            lexeme[1] = '\0';
            output(tmp);
            output("\n");
            f++;
            ///list here

            SaveLexeme:
                b = f;

                itoa(line, tmp, 10);
                fputs((const char*)tmp, token_file);
                fputs("\t", token_file);
                fputs((const char*)lexeme, token_file);
                fputs("\t", token_file);
                itoa(token, tmp, 10);
                fputs((const char*)tmp, token_file);
                fputs("\t", token_file);
                itoa(attribute, tmp, 10);
                fputs((const char*)tmp, token_file);
                fputs("\n", token_file);

            free(lexeme);
            lexeme = nullptr;
        }
        line++;
    }
    fclose(token_file);

    ReservedWordListNode *nxtwrd = reserved_words->head;
    while(nxtwrd != nullptr)
    {
        free(nxtwrd->reserved_word->lexeme);
        nxtwrd->reserved_word->lexeme = nullptr;

        free(nxtwrd->reserved_word);
        nxtwrd->reserved_word = nullptr;

        ReservedWordListNode *tmp = nxtwrd->nxt;

        free(nxtwrd);
        nxtwrd = nullptr;

        nxtwrd = tmp;
    }

    free(reserved_words);
    reserved_words = nullptr;

    SymbolListNode *nxt = symbols->head;
    while(nxt != nullptr)
    {
        Symbol *symbl = nxt->symbol;
        nxt = nxt->nxt;
        cout<<string(symbl->lexeme)<<endl;


        fputs((const char*)symbl->lexeme, symbol_table_file);
        fputs("\t", symbol_table_file);
        fputs((const char*)symbl->token_lexeme, symbol_table_file);
        fputs("\t", symbol_table_file);
        itoa(symbl->token, tmp, 10);
        fputs((const char*)tmp, symbol_table_file);
        fputs("\t", symbol_table_file);
        fputs((const char*)symbl->attribute_lexeme, symbol_table_file);
        fputs("\t", symbol_table_file);
        sprintf(tmp, "%p", &symbl);
        fputs((const char*)tmp, symbol_table_file);
        fputs("\n", symbol_table_file);
    }

    nxt = symbols->head;
    while(nxt != nullptr)
    {
        free(nxt->symbol);
        nxt->symbol = nullptr;

        SymbolListNode *tmp = nxt->nxt;

        free(nxt);
        nxt = nullptr;

        nxt = tmp;
    }

    free(symbols);
    symbols = nullptr;

    free(codeline);
    codeline = nullptr;

    free(tmp);
    tmp = nullptr;

    free(tmp0);
    tmp0 = nullptr;

    fclose(source_code);
    fclose(symbol_table_file);

    return 0;
}
