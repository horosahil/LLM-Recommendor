import { StyleSheet} from 'react-native'
import React from 'react'
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { NavigationContainer } from '@react-navigation/native';
import HomeScreen from './src/screen/HomeScreen'
import LoginScreen from './src/screen/LoginScreen';
import SignupScreen from  './src/screen/SignupScreen';
import LandingScreen from './src/screen/LandingScreen';
import CategoryPage from './src/screen/CategoryPage';
import CartScreen from './src/screen/CartScreen';
import Category from './src/screen/Category';
import { CartProvider } from './src/screen/CartContext';
import Recommendation from './src/screen/Recommendation';


const Stack = createNativeStackNavigator();

const App = () => {
  return (
    <CartProvider>
    <NavigationContainer>
      <Stack.Navigator screenOptions={{headerShown:false,}}>
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="LOGIN" component={LoginScreen} />    
        <Stack.Screen name="SIGNUP" component={SignupScreen}/>
        <Stack.Screen name="LANDING" component={LandingScreen}/>
        <Stack.Screen name="CATEGORY" component={CategoryPage}/>
        <Stack.Screen name="CART" component={CartScreen}/>
        <Stack.Screen name="CATEGORY1" component={Category}/>
        <Stack.Screen name="RECOMMENDATION" component={Recommendation}/>

      </Stack.Navigator>

    </NavigationContainer>
    </CartProvider>
   
  )
}

export default App

const styles = StyleSheet.create({})